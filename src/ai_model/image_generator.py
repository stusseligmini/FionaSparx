#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Generator - Compatibility bridge
"""

from .advanced_image_generator import AdvancedImageGenerator

# Legacy alias
class ImageGenerator(AdvancedImageGenerator):
    """Legacy compatibility wrapper"""
    pass
