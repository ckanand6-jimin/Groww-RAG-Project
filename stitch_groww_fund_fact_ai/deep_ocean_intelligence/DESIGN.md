---
name: Deep Ocean Intelligence
colors:
  surface: '#01142a'
  surface-dim: '#01142a'
  surface-bright: '#293a51'
  surface-container-lowest: '#000f22'
  surface-container-low: '#091c32'
  surface-container: '#0e2036'
  surface-container-high: '#192b41'
  surface-container-highest: '#24364d'
  on-surface: '#d3e3ff'
  on-surface-variant: '#c3c6cf'
  inverse-surface: '#d3e3ff'
  inverse-on-surface: '#203148'
  outline: '#8d9199'
  outline-variant: '#43474e'
  surface-tint: '#a6c9f9'
  primary: '#a6c9f9'
  on-primary: '#043259'
  primary-container: '#133b63'
  on-primary-container: '#83a6d4'
  inverse-primary: '#3d608a'
  secondary: '#44ded4'
  on-secondary: '#003734'
  secondary-container: '#02c2b8'
  on-secondary-container: '#004a46'
  tertiary: '#a2c9ff'
  on-tertiary: '#00315b'
  tertiary-container: '#003b6b'
  on-tertiary-container: '#58a7ff'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d3e4ff'
  primary-fixed-dim: '#a6c9f9'
  on-primary-fixed: '#001c38'
  on-primary-fixed-variant: '#244871'
  secondary-fixed: '#65f8ed'
  secondary-fixed-dim: '#40dcd1'
  on-secondary-fixed: '#00201e'
  on-secondary-fixed-variant: '#00504b'
  tertiary-fixed: '#d3e4ff'
  tertiary-fixed-dim: '#a2c9ff'
  on-tertiary-fixed: '#001c38'
  on-tertiary-fixed-variant: '#004881'
  background: '#01142a'
  on-background: '#d3e3ff'
  surface-variant: '#24364d'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 64px
  container-max: 1440px
  gutter: 24px
---

## Brand & Style
The design system is engineered for a high-fidelity, AI-driven fintech experience. It prioritizes a **"Dark-First"** architecture that evokes a sense of security, depth, and institutional intelligence. The brand personality is professional yet approachable, combining the rigor of financial data with the fluid interaction of modern RAG-based AI.

The visual style is a hybrid of **Modern Corporate** and **Glassmorphism**. It utilizes a sophisticated navy palette to create a low-eye-strain environment, essential for reading complex financial FAQs. Surface layers are defined by subtle translucency and background blurs, creating a "Dashboard-as-an-Appliance" feel that is both premium and technologically advanced.

## Colors
The palette is built on a foundation of deep, layered blues to establish a "Deep Ocean" aesthetic. 

- **Foundation:** The `#07111F` background provides a high-contrast base for the lighter `#102744` card surfaces.
- **Accents:** The **Accent Teal** is used sparingly for primary actions and "Groww-inspired" brand recognition. **Highlight Blue** is reserved for interactive states and AI-driven data visualizations.
- **Functional:** Success and Warning colors are optimized for visibility against dark backgrounds, using high-saturation tones to ensure financial alerts are immediately legible.

## Typography
The system employs a dual-font strategy. **Hanken Grotesk** is used for headlines to provide a sharp, contemporary "fintech-forward" feel. **Inter** handles the heavy lifting of body copy and chat messages, chosen for its exceptional legibility in data-dense environments. 

**JetBrains Mono** is introduced as a utility font for labels and metadata (e.g., timestamps, source citations in RAG responses), reinforcing the "technical/AI" nature of the product. All typography should maintain a high contrast ratio against the dark background, primarily using `text_primary` for headlines and `text_secondary` for long-form reading.

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. The sidebar navigation is fixed at 280px, while the chat and dashboard content area expands to fill the remaining width up to a maximum of 1440px.

- **Grid:** A 12-column system is used for dashboard layouts, while the chat interface centers within an 8-column container for maximum readability.
- **Rhythm:** An 8px linear scale governs all padding and margins. 
- **Responsive:** On mobile devices, the 24px margins scale down to 16px, and the sidebar collapses into a bottom navigation bar or a hamburger-triggered drawer.

## Elevation & Depth
Depth is achieved through **Glassmorphism** and **Tonal Layering** rather than traditional black shadows.

1.  **Level 0 (Background):** Pure `#07111F`.
2.  **Level 1 (Surface):** `#0B1E34` with no blur. Used for structural sidebars.
3.  **Level 2 (Cards):** `#102744` with a 1px border of `rgba(255,255,255,0.08)`.
4.  **Level 3 (Interactive/Overlays):** Glassmorphic surfaces using a 20px Backdrop Blur and 40% opacity on the surface color.

**Shadows:** Shadows are "Soft & Blue," using high-spread, low-opacity hex codes like `rgba(0, 0, 0, 0.4)` combined with a subtle outer glow of the primary navy to make elements feel like they are floating in deep space.

## Shapes
The design system utilizes a **2XL Rounded** philosophy to soften the technical nature of fintech data. 

- **Cards & Chat Bubbles:** Use a 1rem (16px) base radius.
- **Outer Containers:** Main dashboard sections use a 1.5rem (24px) radius.
- **Inputs & Buttons:** Maintain a consistent 0.5rem (8px) radius to differentiate them from the softer container shapes.
- **Buttons:** Primary action buttons can optionally use a pill-shape (3rem) to stand out against rectangular card content.

## Components

### Chat Interface
- **Messages:** AI responses use the `surface_card` background with a subtle teal left-border. User messages use `primary_navy`.
- **Sources:** RAG-sourced links should appear as small, high-contrast chips using the `label-caps` typography.

### Buttons & Inputs
- **Primary Button:** Gradient fill from `secondary_teal` to `highlight_blue`. White text.
- **Search Input:** Floating style with a `rgba(255,255,255,0.05)` fill and a 1px border that glows `highlight_blue` on focus.
- **Glass Chips:** Semi-transparent containers for quick-reply FAQ suggestions.

### Navigation
- **Sidebar:** Darker than the main canvas (`#0B1E34`). Active states are indicated by a vertical teal bar and a subtle background tint.
- **Cards:** Use "2xl" rounded corners with a soft inner stroke to define the edges against the dark background.

### Checkboxes & Radios
- Custom-styled using `secondary_teal` for the checked state, ensuring they pop against the navy surfaces.