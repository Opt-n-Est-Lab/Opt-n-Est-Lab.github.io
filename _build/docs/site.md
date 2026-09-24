---
# ---------------------------------------------------------------------------
# Site-wide settings: written once here, used on every page.
# The header, the nav bar and the footer are all built from this file.
# ---------------------------------------------------------------------------

name: ONE Lab
full_name: Optimization and Estimation Lab
# The two lines under the logo in the header (<br /> starts the second line).
tagline: Optimization and Estimation Laboratory<br />University of New Mexico
department: Mechanical Engineering, University of New Mexico
university: University of New Mexico
room: ME Building, Room 230

email: one@unm.edu        # the lab address
pi_email: wwan@unm.edu    # Dr. Wan's address, used on "Email Dr. Wan" buttons
github: https://github.com/Opt-n-Est-Lab
ga_id: G-SW68LZVXCV       # Google Analytics

# The nav bar, left to right. `short` is the label on narrow screens.
nav:
  - {key: home,         href: ./,                      label: Home,         short: Home}
  - {key: people,       href: people/,                 label: People,       short: People}
  - {key: projects,     href: projects/,               label: Projects,     short: Projects}
  - {key: publications, href: publications/,           label: Publications, short: Pubs}
  - {key: faq,          href: faq/,                    label: FAQ,          short: FAQ}

# Footer icons, in order. `icon` must be one of the names in build.py's ICON.
social:
  - {icon: linkedin, url: "https://www.linkedin.com/company/opt-est-lab/posts", label: ONE Lab on LinkedIn}
  - {icon: github,   url: "https://github.com/Opt-n-Est-Lab",                   label: ONE Lab on GitHub}
  - {icon: youtube,  url: "https://www.youtube.com/@ONE_lab",                   label: ONE Lab on YouTube}
---
