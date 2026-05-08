# -*- coding: utf-8 -*-
"""Base browser driver contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from ..models import BrowserProfile, BrowserProfileStatus


class BrowserDriver(ABC):
    @abstractmethod
    def detect(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        raise NotImplementedError

    @abstractmethod
    def start(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        raise NotImplementedError

    @abstractmethod
    def stop(self, profile: BrowserProfile, runtime_state: Dict[str, Dict[str, object]]) -> BrowserProfileStatus:
        raise NotImplementedError
