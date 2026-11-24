"""테마(스킨) 정의 — html[data-theme] 토큰 CSS, 히트맵 팔레트, 기본 팔레트, 좌우 색.
테마를 추가하려면 SKINS에 항목을 넣고 THEME_ORDER에 키를 추가한 뒤 build.py를 실행한다."""

SKINS = {
  "v1": dict(label="샌드스톤", theme="#f7f1e8", left="#5c6f5d", right="#6b443d",
    tokens="""
[T]{
  color-scheme:light;
  --bg:#f7f1e8; --surface:#fefaef; --surface-2:#efeae2; --surface-3:#e6ded3;
  --line:#e6ded3; --line-2:#dbcdc2; --ink:#1c1c1c; --ink-2:#3f3c37; --ink-3:#6f6c67;
  --accent:#1c1c1c; --accent-soft:#e2edd5; --accent-ink:#f7f1e8; --accent-hover:#2f2d2b;
  --left:#5c6f5d; --right:#6b443d; --blue:#2a72de; --red:#d22c15;
  --note-ink:#6b443d; --hit-bg:#e0512a; --hit-ink:#fff; --ok-bg:#e2edd5; --ok-ink:#5c6f5d;
  --on-ink:#f7f1e8; --ink-hover:#2f2d2b; --glass:rgba(254,250,239,.92); --glass-hover:#fefaef;
  --nav-bg:rgba(247,241,232,.8); --dock-bg:rgba(254,250,239,.88); --card-line:#e6ded3; --stage-bg:#efeae2; --shadow:60,40,30;
  --viz-outline:rgba(28,28,28,.4); --viz-sensor-fill:rgba(254,250,239,.9); --viz-sensor-line:rgba(28,28,28,.55); --viz-cop-fill:#2a72de; --viz-cop-line:#fefaef;
}
[T] .card--why b{color:var(--right)}
[T] .ex-match .ex-card .ex-kind{color:var(--left)}
""",
    palettes={"warm":["#e6ded3","#d6caba","#c0865d","#6b443d","#39221e"],
              "thermal":["#e6ded3","#1b3449","#3e2242","#d22c15","#f2c641","#fffbe6"],
              "jet":["#e6ded3","#00007f","#0000ff","#00ffff","#7fff7f","#ffff00","#ff0000","#7f0000"],
              "olive":["#e6ded3","#c5cfb8","#849671","#5c6f5d","#224228"]},
    default_pal="warm"),
  "v2": dict(label="나이트", theme="#0b1016", left="#5fd4ff", right="#ffb54a",
    tokens="""
[T]{
  color-scheme:dark;
  --bg:#0b1016; --surface:#121922; --surface-2:#1a2330; --surface-3:#26313f;
  --line:rgba(255,255,255,.07); --line-2:rgba(255,255,255,.14); --ink:#f2f5f8; --ink-2:#b9c3cd; --ink-3:#7d8895;
  --accent:#f2f5f8; --accent-soft:rgba(95,212,255,.14); --accent-ink:#0b1016; --accent-hover:#ffffff;
  --left:#5fd4ff; --right:#ffb54a; --blue:#7cc4ff; --red:#ff6b6b;
  --note-ink:#ffd08a; --hit-bg:#ff7a45; --hit-ink:#2a1000; --ok-bg:rgba(95,212,255,.14); --ok-ink:#a9e6ff;
  --on-ink:#0b1016; --ink-hover:#ffffff; --glass:rgba(18,25,34,.86); --glass-hover:#1a2330;
  --nav-bg:rgba(11,16,22,.72); --dock-bg:rgba(18,25,34,.9); --card-line:rgba(255,255,255,.07); --shadow:0,0,0;
  --stage-bg:radial-gradient(ellipse 70% 80% at 50% 55%,#111a24 0%,#080c11 70%);
  --viz-outline:rgba(255,255,255,.28); --viz-sensor-fill:rgba(8,12,17,.75); --viz-sensor-line:rgba(255,255,255,.65); --viz-cop-fill:#ffffff; --viz-cop-line:#080c11;
}
[T] .card--why b{color:var(--left)}
[T] .ex-match .ex-card .ex-kind{color:var(--left)}
[T] .dock-in,[T] .stage-pop{border:1px solid var(--line-2)}
[T] .chip,[T] .stage-foot span{border:1px solid var(--line)}
""",
    palettes={"ember":["#1a2330","#3b1f4e","#8b2c5a","#e0553a","#ffb54a","#fff3c4"],
              "ice":["#1a2330","#123a5c","#1f6f9e","#5fd4ff","#c9f2ff","#ffffff"],
              "jet":["#1a2330","#00007f","#0000ff","#00ffff","#7fff7f","#ffff00","#ff0000","#7f0000"],
              "mono":["#1a2330","#2b4a5c","#3f7f95","#6fb9cf","#b9ecff"]},
    default_pal="ember"),
  "v3": dict(label="코발트", theme="#f1f2f4", left="#0d0e12", right="#2f4dff",
    tokens="""
[T]{color-scheme:light}
""",
    palettes={"plasma":["#e3e5ea","#c4caff","#7d6cff","#c94fb0","#ff6a3d","#ffc83d"],
              "cobalt":["#e3e5ea","#c9d0ff","#8290ff","#3f57ff","#1b2fb8","#0d0e12"],
              "heat":["#e3e5ea","#ffd9c2","#ff8a4c","#e5484d","#7a1b3a"],
              "jet":["#e3e5ea","#00007f","#0000ff","#00ffff","#7fff7f","#ffff00","#ff0000","#7f0000"]},
    default_pal="plasma"),
  "v4": dict(label="세이지", theme="#f2f5f1", left="#0f6e63", right="#ff6b3d",
    tokens="""
[T]{
  color-scheme:light;
  --bg:#f2f5f1; --surface:#ffffff; --surface-2:#f2f6f2; --surface-3:#e1e8e1;
  --line:#e1e8e1; --line-2:#cbd6cc; --ink:#12201c; --ink-2:#4a5a55; --ink-3:#83928c;
  --accent:#0f6e63; --accent-soft:#dcf0ea; --accent-ink:#ffffff; --accent-hover:#0b5a51;
  --left:#0f6e63; --right:#ff6b3d; --blue:#0f6e63; --red:#e5484d;
  --note-ink:#83928c; --hit-bg:#e8481f; --hit-ink:#fff; --ok-bg:#dcf0ea; --ok-ink:#0f6e63;
  --on-ink:#ffffff; --ink-hover:#243530; --glass:rgba(255,255,255,.92); --glass-hover:#ffffff;
  --nav-bg:rgba(242,245,241,.8); --dock-bg:rgba(255,255,255,.88); --card-line:transparent; --stage-bg:#eef3ee; --shadow:18,32,28;
  --viz-outline:rgba(18,32,28,.18); --viz-sensor-fill:#ffffff; --viz-sensor-line:rgba(18,32,28,.4); --viz-cop-fill:#ff6b3d; --viz-cop-line:#ffffff;
}
[T] .card--why b{color:var(--right)}
""",
    palettes={"moss":["#dfe6df","#c8e3d4","#6bb896","#0f6e63","#0a3d38","#12201c"],
              "sunset":["#dfe6df","#ffe1c2","#ff9a5c","#ff6b3d","#b8173a","#3a0b1a"],
              "jet":["#dfe6df","#00007f","#0000ff","#00ffff","#7fff7f","#ffff00","#ff0000","#7f0000"],
              "slate":["#dfe6df","#c3cfcc","#8aa19c","#4a5a55","#12201c"]},
    default_pal="moss"),
}
THEME_ORDER = ["v4", "v1", "v2", "v3"]
THEME_DEFAULT = "v4"
PAL_LABELS = {"warm":"웜","thermal":"서멀","jet":"제트","olive":"올리브","ember":"엠버","ice":"아이스","mono":"단색",
              "plasma":"플라즈마","cobalt":"코발트","heat":"히트","moss":"모스","sunset":"선셋","slate":"슬레이트"}
def scoped(k):
    return SKINS[k]["tokens"].replace("[T]", 'html[data-theme="' + k + '"]')
