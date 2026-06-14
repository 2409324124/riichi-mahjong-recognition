"""
计分系统模块

实现日本立直麻将的计分逻辑，包括：
- 役种识别
- 符数计算
- 点数计算
"""

from .yaku import Yaku, YakuType
from .fu import FuCalculator
from .score import ScoreCalculator, ScoreResult