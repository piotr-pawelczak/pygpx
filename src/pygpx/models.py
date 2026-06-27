from pydantic import BaseModel
import datetime


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class TrackPoint(BaseModel):
    coordinates: Coordinates
    elevation: float | None = None
    timestamp: datetime.datetime | None = None
    heart_rate: int | None = None
    temperature: float | None = None


class TrackSegment(BaseModel):
    points: list[TrackPoint]


class Track(BaseModel):
    name: str | None = None
    type: str | None = None
    segments: list[TrackSegment]
