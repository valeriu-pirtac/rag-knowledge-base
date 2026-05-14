"""S3-compatible storage adapter using aioboto3."""

import hashlib
from collections.abc import AsyncIterator
from uuid import UUID

import aioboto3  # type: ignore[import-untyped]
import structlog

from application.interfaces import StorageInterface
from configuration.storage import StorageConfig


log = structlog.get_logger(__name__)

_MIN_PART_SIZE = 5 * 1024 * 1024  # 5 MB minimum for S3 multipart


class S3StorageAdapter(StorageInterface):
    """Adapter for Garbage S3-compatible object storage."""

    def __init__(self, config: StorageConfig) -> None:
        self._config = config
        self._endpoint_url = f"{config.protocol}://{config.host}:{config.s3_port}"
        self._bucket = config.bucket_name
        self._bucket_ensured = False

    async def _ensure_bucket_once(self) -> None:
        if not self._bucket_ensured:
            await self.ensure_bucket()
            self._bucket_ensured = True

    async def store(self, key: str, data: bytes) -> str:
        await self._ensure_bucket_once()
        session = aioboto3.Session()
        async with session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._config.access_key_id,
            aws_secret_access_key=self._config.access_key_secret.get_secret_value(),
            config={
                "retries": {"max_attempts": 3, "mode": "standard"},
                "connect_timeout": self._config.timeout,
                "read_timeout": self._config.timeout,
            },
        ) as client:
            await client.put_object(Bucket=self._bucket, Key=key, Body=data)
        return key

    async def store_stream(self, key: str, stream: AsyncIterator[bytes]) -> str:
        await self._ensure_bucket_once()
        session = aioboto3.Session()
        async with session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._config.access_key_id,
            aws_secret_access_key=self._config.access_key_secret.get_secret_value(),
            config={
                "retries": {"max_attempts": 3, "mode": "standard"},
                "connect_timeout": self._config.timeout,
                "read_timeout": self._config.timeout,
            },
        ) as client:
            mpu = await client.create_multipart_upload(Bucket=self._bucket, Key=key)
            upload_id = mpu["UploadId"]

            parts: list[dict[str, str | int]] = []
            part_number = 1
            sha256 = hashlib.sha256()
            total_size = 0

            async for chunk in stream:
                sha256.update(chunk)
                total_size += len(chunk)
                part = await client.upload_part(
                    Bucket=self._bucket,
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk,
                )
                parts.append({"ETag": part["ETag"], "PartNumber": part_number})
                part_number += 1

            if total_size == 0:
                await client.abort_multipart_upload(Bucket=self._bucket, Key=key, UploadId=upload_id)
                return key

            await client.complete_multipart_upload(
                Bucket=self._bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
        return key

    async def ensure_bucket(self) -> None:
        session = aioboto3.Session()
        async with session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._config.access_key_id,
            aws_secret_access_key=self._config.access_key_secret.get_secret_value(),
        ) as client:
            try:
                await client.head_bucket(Bucket=self._bucket)
            except Exception:
                log.info("Bucket not found, creating", bucket=self._bucket)
                try:
                    await client.create_bucket(Bucket=self._bucket)
                    log.info("Bucket created", bucket=self._bucket)
                except Exception as exc:
                    log.error("Failed to create bucket", bucket=self._bucket, error=str(exc))

    def build_key(self, workspace_id: UUID, document_id: UUID, mime_type: str | None) -> str:
        """Build the S3 object key for a document."""
        if mime_type:
            subtype = mime_type.split("/")[-1]
            return f"bronze/{workspace_id}/raw_documents/{subtype}/{document_id}"
        return f"bronze/{workspace_id}/raw_documents/unknown/{document_id}"
