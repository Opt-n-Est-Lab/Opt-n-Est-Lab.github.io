---
# The People page: the header block, then each group in the order below.
#
# Per person (only name, photo and dept are required):
#   honors    - list of lines in link colour with an award icon
#   interests - the research-interest badge at the foot of the card
#   website, github, linkedin, email, ... - the icon links
#   row: true - show as a one-line alumni row instead of a card
#               (uses degree and nxt, the next position)

title: Team
intro: |
  The ONE Lab brings together students from ME, ECE, CS, and Math departments, along with high-school interns and visiting/exchange scholars and students.

  We’re always seeking highly motivated and energetic individuals to join our team.

card:
  title: Join us
  text: We welcome applicants prepared in controls, optimization, applied mathematics, and/or machine learning.
  button: Current Openings
  link: faq/

# The empty "You can be here" card, placed at the end of one group.
join_card:
  section: "Interns and Visiting Scholars"
  name: "You can be here"
  dept: "Join Us"
  label: "Read the FAQ"
  href: faq/

groups:

- title: "Professors"
  members:
    - name: "Wenbin Wan"
      lead: true
      photo: "pic/profile/wwan_pro.png"
      dept: "Assistant Professor, Mechanical Engineering"
      email: "wwan@unm.edu"
      website: "https://wenbinwan.com/"
      scholar: "https://scholar.google.com/citations?hl=en&amp;user=lHPbcs8AAAAJ&amp;view_op=list_works&amp;sortby=pubdate"
      researchgate: "https://www.researchgate.net/profile/Wenbin-Wan"
      orcid: "https://orcid.org/0000-0002-4920-2215"
      x: "https://twitter.com/__WWan"
      github: "https://github.com/wbinw"
      arxiv: "https://arxiv.org/search/?query=Wan%2C+Wenbin&amp;searchtype=all&amp;abstracts=show&amp;order=-announced_date_first&amp;size=50"
      linkedin: "https://www.linkedin.com/in/wenbinwan/"
      bio: >-
        <a href="https://wenbinwan.com/" target="_blank" rel="noopener noreferrer"><strong>Wenbin
        Wan</strong></a> is an Assistant Professor in the Department of Mechanical Engineering at the
        University of New Mexico (UNM). He received his Ph.D. in mechanical engineering and his M.S. in
        applied mathematics from the University of Illinois Urbana-Champaign (UIUC). He earned a B.S. in
        mechanical engineering from the University of Missouri–Columbia. He was appointed as a MechSE
        Teaching Fellow at UIUC, named a CPS Rising Star by the University of Virginia. He was selected
        as an NM SPARK Scholar at UNM.

- title: "PhD Students"
  members:
    - name: "Kumar Anurag"
      photo: "pic/profile/kumar_anurag.jpg"
      dept: "Mechanical Engineering"
      email: "kmranrg@unm.edu"
      interests: "Reservoir Computing"
      website: "https://kan.phd"
      github: "https://github.com/kmranrg"
      linkedin: "https://www.linkedin.com/in/kmranrg/"
    - name: "Abel Molinar"
      photo: "pic/profile/abel_molinar.jpg"
      dept: "Mechanical Engineering"
      email: "amolinar@unm.edu"
      honors: ["NSF Graduate Research Fellow", "NSF RAISE Fellow"]
      interests: "Nonlinear Filter"
      website: "https://abelmolinar.github.io/"
      github: "https://github.com/abelmolinar"
      linkedin: "https://www.linkedin.com/in/abel-molinar-41212532b/"
    - name: "Seif Osama"
      photo: "pic/profile/seif_osama.jpg"
      dept: "Mechanical Engineering"
      email: "selsabagh@unm.edu"
      interests: "Distributional Robustness"
      github: "https://github.com/SeifO070"
      linkedin: "https://www.linkedin.com/in/seif-osama/"

- title: "Master Students"
  members:
    - name: "Isaiah Candelaria"
      photo: "pic/profile/isaiah_candelaria.png"
      dept: "Electrical and Computer Engineering"
      email: "ican@unm.edu"
      honors: ["NSF RAISE Fellow"]
      interests: "Neural Networks"
      github: "https://github.com/IsaiahCandelaria"
      linkedin: "https://www.linkedin.com/in/isaiah-candelaria-73667b29a/"

- title: "Undergrad Students"
  members:
    - name: "Brady Kissinger"
      photo: "pic/profile/brady_kissinger.jpg"
      dept: "Mechanical Engineering"
      email: "bkissinger@unm.edu"
      interests: "UAV Tracking in VR"
      github: "https://github.com/Bkissinger03"
      linkedin: "https://www.linkedin.com/in/brady-kissinger-104268326"
    - name: "Joshua Barton"
      photo: "pic/profile/joshua_barton.jpg"
      dept: "Mechanical Engineering"
      email: "bartonj@unm.edu"
      interests: "F1/10 Self-driving Car"
      github: "https://github.com/JBarton02"
      linkedin: "https://www.linkedin.com/in/joshua-barton-062973187"
    - name: "Ankit Devarapalli"
      photo: "pic/profile/ankit_devarapalli.jpg"
      dept: "Computer Science"
      email: "anki2006@unm.edu"
      interests: "UAV Tracking in VR"
      github: "https://github.com/devbyankit"
      linkedin: "https://www.linkedin.com/in/ankit-devarapalli-a6562b305/"
    - name: "Cuyler Gordon"
      photo: "pic/profile/cuyler_gordon.jpg"
      dept: "Computer Science"
      email: "cgordon4@unm.edu"
      interests: "UAV Tracking in VR"
      github: "https://github.com/Cgor4"
      linkedin: "https://www.linkedin.com/in/cuyler-d-gordon/"
    - name: "Haasika Jagirapu"
      photo: "pic/profile/haasika_jagirapu.jpg"
      dept: "Computer Science"
      email: "hjagirapu@unm.edu"
      interests: "Reservoir Computing"
      github: "https://github.com/haasikaj"
      linkedin: "https://www.linkedin.com/in/hjagirapu/"

- title: "Interns and Visiting Scholars"
  members: []

- title: "Alumni"
  members:
    - name: "Huy Dinh"
      photo: "pic/profile/alumni/huy_dinh_25.jpg"
      dept: "AIMS@UNM"
      degree: "UNM, Intern (High School) &rsquo;25"
      nxt: "B.S. program at UNM"
      linkedin: "https://www.linkedin.com/in/huy-dinh-82295336a"
      row: true
    - name: "Samir Giri"
      photo: "pic/profile/alumni/samir_giri_26.jpg"
      dept: "Mechanical Engineering"
      degree: "UNM, B.S. &rsquo;26"
      interests: "Motion Planning"
      nxt: "OVPR Information Technology Support"
      github: "https://github.com/Samir739"
      linkedin: "https://www.linkedin.com/in/samir-giri-754227271"
      row: true
    - name: "Hanyu Hao"
      photo: "pic/profile/alumni/hanyu_hao_25.jpg"
      dept: "Mathematics and Statistics"
      degree: "UNM, B.S. &rsquo;25"
      interests: "Racing car dynamics and control"
      nxt: "M.S. program at Clemson University"
      linkedin: "https://www.linkedin.com/in/hanyu-hao-746461281"
      row: true
    - name: "Abel Molinar"
      photo: "pic/profile/alumni/abel_molinar_25.png"
      dept: "Mechanical Engineering"
      degree: "UNM, B.S. &rsquo;25"
      interests: "Nonlinear Filter"
      nxt: "Ph.D. program at UNM (NSF GRFP &rsquo;25)"
      github: "https://github.com/aim017"
      linkedin: "https://www.linkedin.com/in/abel-molinar-41212532b/"
      row: true
---
