"""
Unified Color Palette Generator for Dark Theme Consistency
Provides a centralized color system for the trading analytics platform
"""

import json
from typing import Dict, Tuple, List


class ColorPalette:
    """Generates and manages a unified color palette for dark theme consistency"""
    
    def __init__(self):
        # Base colors with semantic meanings
        self.base_colors = {
            # Primary brand colors
            'primary': '#60a5fa',      # Sky blue - main brand color
            'primary_dark': '#3b82f6', # Darker blue for depth
            'primary_light': '#93c5fd', # Lighter blue for highlights
            
            # Secondary accent colors
            'secondary': '#8b5cf6',     # Purple - secondary actions
            'secondary_dark': '#7c3aed', # Dark purple
            'secondary_light': '#a78bfa', # Light purple
            
            # Status/semantic colors
            'success': '#10b981',       # Green - positive/profits
            'success_dark': '#059669',
            'success_light': '#34d399',
            
            'warning': '#f59e0b',       # Amber - caution/medium
            'warning_dark': '#d97706',
            'warning_light': '#fbbf24',
            
            'danger': '#ef4444',        # Red - negative/losses
            'danger_dark': '#dc2626',
            'danger_light': '#f87171',
            
            'info': '#06b6d4',          # Cyan - informational
            'info_dark': '#0891b2',
            'info_light': '#22d3ee',
            
            # Neutral colors for backgrounds and text
            'background': '#0a0a0a',    # Main dark background
            'surface': '#18181b',       # Card/component background
            'surface_hover': '#27272a', # Hover states
            'border': '#27272a',        # Default borders
            'border_light': '#3f3f46',  # Emphasized borders
            
            # Text hierarchy
            'text_primary': '#f4f4f5',   # Main text
            'text_secondary': '#a1a1aa', # Secondary text
            'text_muted': '#71717a',     # Muted/disabled text
            'text_bright': '#ffffff',    # Emphasized text
        }
        
        # Trading-specific color mappings
        self.trading_colors = {
            'buy': self.base_colors['success'],
            'sell': self.base_colors['danger'],
            'hold': self.base_colors['warning'],
            'profit': self.base_colors['success'],
            'loss': self.base_colors['danger'],
            'breakeven': self.base_colors['warning'],
        }
        
        # Confidence level mappings
        self.confidence_colors = {
            'high': self.base_colors['success'],      # 80-100%
            'medium': self.base_colors['warning'],    # 50-79%
            'low': self.base_colors['danger'],        # 0-49%
        }
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def generate_alpha_variant(self, hex_color: str, alpha: float) -> str:
        """Generate RGBA color with specified alpha"""
        r, g, b = self.hex_to_rgb(hex_color)
        return f'rgba({r}, {g}, {b}, {alpha})'
    
    def generate_gradient(self, color1: str, color2: str, angle: int = 135) -> str:
        """Generate CSS gradient between two colors"""
        return f'linear-gradient({angle}deg, {color1} 0%, {color2} 100%)'
    
    def generate_glow_effect(self, hex_color: str, intensity: float = 0.5) -> str:
        """Generate CSS glow/shadow effect"""
        r, g, b = self.hex_to_rgb(hex_color)
        return f'0 0 30px rgba({r}, {g}, {b}, {intensity})'
    
    def get_color_variants(self, base_color: str) -> Dict[str, str]:
        """Generate color variants (lighter/darker) from base color"""
        r, g, b = self.hex_to_rgb(base_color)
        
        # Lighter variant (20% lighter)
        lighter = self.rgb_to_hex((
            min(255, int(r * 1.2)),
            min(255, int(g * 1.2)),
            min(255, int(b * 1.2))
        ))
        
        # Darker variant (20% darker)
        darker = self.rgb_to_hex((
            int(r * 0.8),
            int(g * 0.8),
            int(b * 0.8)
        ))
        
        return {
            'base': base_color,
            'light': lighter,
            'dark': darker,
            'alpha_10': self.generate_alpha_variant(base_color, 0.1),
            'alpha_20': self.generate_alpha_variant(base_color, 0.2),
            'alpha_50': self.generate_alpha_variant(base_color, 0.5),
            'glow': self.generate_glow_effect(base_color)
        }
    
    def get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence percentage"""
        if confidence >= 80:
            return self.confidence_colors['high']
        elif confidence >= 50:
            return self.confidence_colors['medium']
        else:
            return self.confidence_colors['low']
    
    def get_profit_loss_color(self, value: float) -> str:
        """Get color based on profit/loss value"""
        if value > 0:
            return self.trading_colors['profit']
        elif value < 0:
            return self.trading_colors['loss']
        else:
            return self.trading_colors['breakeven']
    
    def generate_css_variables(self) -> str:
        """Generate CSS custom properties for all colors"""
        css_vars = [":root {"]
        
        # Base colors
        css_vars.append("  /* Base Colors */")
        for name, color in self.base_colors.items():
            css_vars.append(f"  --color-{name.replace('_', '-')}: {color};")
        
        # Alpha variants
        css_vars.append("\n  /* Alpha Variants */")
        for name, color in self.base_colors.items():
            if not name.startswith(('text', 'background', 'surface')):
                css_vars.append(f"  --color-{name.replace('_', '-')}-10: {self.generate_alpha_variant(color, 0.1)};")
                css_vars.append(f"  --color-{name.replace('_', '-')}-20: {self.generate_alpha_variant(color, 0.2)};")
                css_vars.append(f"  --color-{name.replace('_', '-')}-50: {self.generate_alpha_variant(color, 0.5)};")
        
        # Gradients
        css_vars.append("\n  /* Gradients */")
        css_vars.append(f"  --gradient-primary: {self.generate_gradient(self.base_colors['primary_dark'], self.base_colors['primary'])};")
        css_vars.append(f"  --gradient-success: {self.generate_gradient(self.base_colors['success_dark'], self.base_colors['success'])};")
        css_vars.append(f"  --gradient-warning: {self.generate_gradient(self.base_colors['warning_dark'], self.base_colors['warning'])};")
        css_vars.append(f"  --gradient-danger: {self.generate_gradient(self.base_colors['danger_dark'], self.base_colors['danger'])};")
        css_vars.append(f"  --gradient-info: {self.generate_gradient(self.base_colors['info_dark'], self.base_colors['info'])};")
        css_vars.append(f"  --gradient-dark: {self.generate_gradient(self.base_colors['surface'], self.base_colors['background'])};")
        
        # Glow effects
        css_vars.append("\n  /* Glow Effects */")
        for name in ['primary', 'success', 'warning', 'danger', 'info']:
            css_vars.append(f"  --glow-{name}: {self.generate_glow_effect(self.base_colors[name])};")
        
        css_vars.append("}")
        return "\n".join(css_vars)
    
    def export_palette(self, format: str = 'json') -> str:
        """Export color palette in various formats"""
        if format == 'json':
            return json.dumps({
                'base_colors': self.base_colors,
                'trading_colors': self.trading_colors,
                'confidence_colors': self.confidence_colors
            }, indent=2)
        elif format == 'css':
            return self.generate_css_variables()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def validate_contrast(self, foreground: str, background: str) -> float:
        """Calculate contrast ratio between two colors (WCAG compliance)"""
        def luminance(rgb):
            r, g, b = [x/255.0 for x in rgb]
            r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
            g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
            b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = luminance(self.hex_to_rgb(foreground))
        l2 = luminance(self.hex_to_rgb(background))
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)


# Singleton instance
color_palette = ColorPalette()


# Helper functions for use in templates and routes
def get_trading_color(action: str) -> str:
    """Get color for trading action (buy/sell/hold)"""
    return color_palette.trading_colors.get(action.lower(), color_palette.base_colors['info'])


def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence percentage"""
    return color_palette.get_confidence_color(confidence)


def get_profit_loss_color(value: float) -> str:
    """Get color based on profit/loss value"""
    return color_palette.get_profit_loss_color(value)


def generate_chart_colors(count: int) -> List[str]:
    """Generate a list of colors for charts"""
    chart_colors = [
        color_palette.base_colors['primary'],
        color_palette.base_colors['success'],
        color_palette.base_colors['warning'],
        color_palette.base_colors['danger'],
        color_palette.base_colors['info'],
        color_palette.base_colors['secondary'],
    ]
    
    # Repeat colors if needed
    while len(chart_colors) < count:
        chart_colors.extend(chart_colors)
    
    return chart_colors[:count]


if __name__ == "__main__":
    # Example usage
    palette = ColorPalette()
    
    # Generate CSS variables
    print("CSS Variables:")
    print(palette.generate_css_variables())
    
    # Test color functions
    print("\nTrading Colors:")
    print(f"Buy: {get_trading_color('buy')}")
    print(f"Sell: {get_trading_color('sell')}")
    
    print("\nConfidence Colors:")
    print(f"90% confidence: {get_confidence_color(90)}")
    print(f"60% confidence: {get_confidence_color(60)}")
    print(f"30% confidence: {get_confidence_color(30)}")
    
    print("\nProfit/Loss Colors:")
    print(f"+$100: {get_profit_loss_color(100)}")
    print(f"-$50: {get_profit_loss_color(-50)}")
    print(f"$0: {get_profit_loss_color(0)}")