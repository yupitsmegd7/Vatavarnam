/**
 * JS-side mirror of the CSS custom properties defined in variables.css.
 * Useful anywhere a component needs a raw value instead of a var() reference —
 * e.g. passing a color into a canvas/SVG library, doing color math in JS,
 * or configuring a charting library that doesn't understand CSS variables.
 *
 * Keep this in sync with variables.css by hand; there are only a handful
 * of tokens, so a build-time generator would be overkill here.
 */

export const theme = {
  colors: {
    // Surfaces
    bgOuter: '#0d0d0d',
    bgSidebar: '#0d0d0d',
    bgCard: '#d9cbc9',
    bgCardSoft: '#cfc0be',
    bgPanelItem: '#ffffff',

    // Text
    textHeading: '#262338',
    textBody: '#3a3550',
    textMuted: '#7c7690',
    textOnDark: '#ffffff',
    textOnDarkMuted: '#a8a4b5',

    // Accents
    accentBlue: '#3556e8',
    accentBlueSoft: '#b7c1ee',
    accentGreen: '#3ec28f',
    track: '#e3dcdb',

    // Icon badges
    iconBlue: '#35a7e8',
    iconPurple: '#9b4fd6',
    iconGreen: '#3ec26b',
    iconOrange: '#f0932b',
    iconNavy: '#2c3178',
  },

  radius: {
    xl: '32px',
    lg: '20px',
    md: '14px',
    full: '999px',
  },

  spacing: {
    1: '4px',
    2: '8px',
    3: '12px',
    4: '16px',
    5: '24px',
    6: '32px',
    7: '48px',
  },

  font: {
    base: "'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
};

export default theme;