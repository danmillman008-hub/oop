#!/usr/bin/env python3
"""Generate the five original SVG environments and the two overlay props."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "lighthouse" / "assets"
SETS = ROOT / "sets"
PROPS = ROOT / "props"
SETS.mkdir(parents=True, exist_ok=True)
PROPS.mkdir(parents=True, exist_ok=True)

# Each background uses layered vector shapes and both linear and radial gradients.
svgs = {
"lighthouse-interior.svg": '''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<defs>
 <linearGradient id="wall" x1="0" y1="0" x2="0.9" y2="1"><stop stop-color="#17283c"/><stop offset="1" stop-color="#30475a"/></linearGradient>
 <linearGradient id="glass" x1="0" y1="0" x2="0.8" y2="1"><stop stop-color="#304b61"/><stop offset="1" stop-color="#102338"/></linearGradient>
 <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#674b3e"/><stop offset="1" stop-color="#302d33"/></linearGradient>
 <radialGradient id="lamp"><stop stop-color="#ffe3a1" stop-opacity=".95"/><stop offset=".28" stop-color="#ffc56b" stop-opacity=".34"/><stop offset="1" stop-color="#f4b856" stop-opacity="0"/></radialGradient>
</defs>
<rect width="1280" height="720" fill="url(#wall)"/>
<path d="M0 490H1280V720H0Z" fill="url(#floor)"/>
<path d="M685 520V259a208 190 0 0 1 416 0v261Z" fill="#111d2d" stroke="#a77d54" stroke-width="21"/>
<path d="M713 500V261a180 162 0 0 1 360 0v239Z" fill="url(#glass)"/>
<path d="M714 401Q890 346 1072 402v35Q888 389 714 439Z" fill="#718995" opacity=".72"/>
<path d="M714 461Q890 421 1072 461v39H714Z" fill="#526d7d" opacity=".8"/>
<path d="M894 96V502M715 286H1072" stroke="#aa825a" stroke-width="14"/>
<path d="M0 580H1280" stroke="#182331" stroke-width="18" opacity=".7"/>
<path d="M0 601H1280M0 662H1280" stroke="#8e6545" stroke-width="4" opacity=".62"/>
<path d="M78 84H600M78 88H600M58 196H470M74 300H600M52 401H540" stroke="#566171" stroke-width="5" opacity=".48"/>
<path d="M110 94v88m155-88v88m171-88v88M96 207v75m148-75v75m143-75v75m126-75v75M70 312v76m170-76v76m174-76v76" stroke="#101d2e" stroke-width="5" opacity=".5"/>
<ellipse cx="910" cy="215" rx="270" ry="220" fill="url(#lamp)"/>
<path d="M93 487H586L548 438H136Z" fill="#4b3732" stroke="#b88558" stroke-width="6"/>
<path d="M132 490v130m408-130v130" stroke="#332c31" stroke-width="18"/>
<rect x="178" y="408" width="105" height="70" rx="5" fill="#9b7048" stroke="#302a31" stroke-width="7"/>
<path d="M188 420h84m-84 12h84m-84 12h84m-84 12h84" stroke="#e6c38a" stroke-width="3"/>
<path d="M310 460l79-36 97 31-71 34Z" fill="#e0cfaa" stroke="#302a31" stroke-width="5"/>
<path d="M332 451l58-19m-48 31 71-23m-45 34 48-16" stroke="#758078" stroke-width="4"/>
<rect x="1142" y="111" width="62" height="165" rx="12" fill="#334250" stroke="#a77d54" stroke-width="6"/>
<path d="M1154 116h37l-5-47h-27Z" fill="#c7945a"/>
<path d="M1160 88h24" stroke="#ffe0a0" stroke-width="6"/>
<circle cx="1172" cy="198" r="17" fill="#ffd582"/>
<path d="M1125 282h98" stroke="#c99b61" stroke-width="8"/>
<path d="M0 524H1280" stroke="#c9a46d" stroke-width="4" opacity=".25"/>
</svg>''',
"lighthouse-window.svg": '''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<defs>
 <linearGradient id="storm" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#111d36"/><stop offset=".55" stop-color="#31465c"/><stop offset="1" stop-color="#172c43"/></linearGradient>
 <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#315c71"/><stop offset="1" stop-color="#101f32"/></linearGradient>
 <linearGradient id="stone" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#384451"/><stop offset="1" stop-color="#1b2838"/></linearGradient>
 <radialGradient id="flash"><stop stop-color="#e8f5ff" stop-opacity=".8"/><stop offset="1" stop-color="#9fb9d4" stop-opacity="0"/></radialGradient>
</defs>
<rect width="1280" height="720" fill="url(#storm)"/>
<ellipse cx="927" cy="196" rx="380" ry="285" fill="url(#flash)"/>
<path d="M0 420Q110 385 220 420T440 420T660 420T880 420T1100 420T1320 420V720H0Z" fill="url(#sea)"/>
<path d="M0 490q70-35 140 0t140 0t140 0t140 0t140 0t140 0t140 0t140 0t140 0t140 0" fill="none" stroke="#9cb4c4" stroke-width="6" opacity=".7"/>
<path d="M0 565q80-28 160 0t160 0t160 0t160 0t160 0t160 0t160 0t160 0" fill="none" stroke="#658296" stroke-width="5" opacity=".72"/>
<path d="M0 640q65-25 130 0t130 0t130 0t130 0t130 0t130 0t130 0t130 0t130 0t130 0" fill="none" stroke="#425f74" stroke-width="5"/>
<path d="M173 720V287a240 205 0 0 1 480 0v433Z" fill="#101927" stroke="#a7815c" stroke-width="30"/>
<path d="M207 700V288a206 174 0 0 1 412 0v412Z" fill="url(#storm)" stroke="#d0aa77" stroke-width="8"/>
<path d="M413 87V702M207 438H619" stroke="#a7815c" stroke-width="19"/>
<path d="M818 90l-79 169h57l-63 159 150-205h-71l62-123Z" fill="#e7f1fb" stroke="#fff7d8" stroke-width="7"/>
<path d="M0 34H1280M0 47H1280" stroke="#607080" stroke-width="13" opacity=".6"/>
<path d="M690 0H1280V47H690Z" fill="url(#stone)"/>
<path d="M690 670H1280V720H690Z" fill="url(#stone)"/>
<path d="M0 125l340 560M54 20l300 540M965 4L715 600M1117 0L865 570M1248 72L1004 570M584 20L421 345M742 40L617 364M105 187L294 514M541 20L400 300M1173 205L952 653M1214 352L1080 635" stroke="#b4cad5" stroke-width="4" opacity=".58"/>
<path d="M775 662h410" stroke="#d1a16a" stroke-width="22"/>
<rect x="0" y="0" width="1280" height="720" fill="none" stroke="#0d1727" stroke-width="30"/>
</svg>''',
"lighthouse-beam.svg": '''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<defs>
 <linearGradient id="darkstone" x1="0" y1="0" x2="0.2" y2="1"><stop stop-color="#152338"/><stop offset="1" stop-color="#293a49"/></linearGradient>
 <linearGradient id="beam" x1="0" y1="0" x2="1" y2=".2"><stop stop-color="#ffdd8c" stop-opacity=".62"/><stop offset="1" stop-color="#ffcc6b" stop-opacity="0"/></linearGradient>
 <radialGradient id="core"><stop stop-color="#fff4c6"/><stop offset=".32" stop-color="#ffd276" stop-opacity=".86"/><stop offset="1" stop-color="#ffbe57" stop-opacity="0"/></radialGradient>
 <linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#30566a"/><stop offset="1" stop-color="#111f32"/></linearGradient>
</defs>
<rect width="1280" height="720" fill="url(#darkstone)"/>
<path d="M0 570H1280V720H0Z" fill="#282b34"/>
<path d="M0 586H1280M0 636H1280M0 685H1280" stroke="#87684d" stroke-width="5" opacity=".55"/>
<path d="M0 170H1280M0 274H1280M0 380H1280M0 477H1280" stroke="#526171" stroke-width="5" opacity=".52"/>
<path d="M66 0V574M241 0V574M1063 0V574M1217 0V574" stroke="#101b2b" stroke-width="15" opacity=".65"/>
<path d="M685 550V258a205 180 0 0 1 410 0v292Z" fill="#0e1b2b" stroke="#a57d55" stroke-width="22"/>
<path d="M714 531V260a176 153 0 0 1 352 0v271Z" fill="url(#water)"/>
<path d="M713 392q176-55 354 2v35q-178-38-354 6Z" fill="#7896a1" opacity=".66"/>
<path d="M891 111V530M713 300H1067" stroke="#9f7954" stroke-width="13"/>
<path d="M351 197L936 285L350 374Z" fill="url(#beam)"/>
<ellipse cx="325" cy="285" rx="255" ry="255" fill="url(#core)"/>
<rect x="277" y="165" width="96" height="231" rx="18" fill="#263746" stroke="#efc676" stroke-width="12"/>
<path d="M293 182h64v190h-64Z" fill="url(#core)"/>
<path d="M258 162h133M258 399h133M284 145h120M284 416h120" stroke="#e9bd72" stroke-width="11"/>
<path d="M306 143V108h39v35M299 422h54v52h-54Z" fill="#b28251"/>
<path d="M298 251h53M298 305h53" stroke="#fff0bd" stroke-width="5" opacity=".75"/>
<path d="M157 533H535" stroke="#d6a966" stroke-width="8" opacity=".7"/>
<path d="M0 28H1280" stroke="#6c7881" stroke-width="12"/>
</svg>''',
"sea-view.svg": '''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<defs>
 <linearGradient id="night" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#131f38"/><stop offset=".6" stop-color="#465b70"/><stop offset="1" stop-color="#e1a36d"/></linearGradient>
 <linearGradient id="ocean" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#315a70"/><stop offset="1" stop-color="#101d31"/></linearGradient>
 <radialGradient id="moonGlow"><stop stop-color="#ffe6ae" stop-opacity=".55"/><stop offset="1" stop-color="#ffd88b" stop-opacity="0"/></radialGradient>
 <linearGradient id="hull" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#533f39"/><stop offset="1" stop-color="#171f2b"/></linearGradient>
</defs>
<rect width="1280" height="720" fill="url(#night)"/>
<ellipse cx="932" cy="160" rx="210" ry="160" fill="url(#moonGlow)"/>
<circle cx="932" cy="160" r="53" fill="#f3dfb2"/>
<circle cx="155" cy="102" r="3" fill="#f5e8c8"/><circle cx="260" cy="169" r="4" fill="#f5e8c8"/><circle cx="492" cy="77" r="3" fill="#f5e8c8"/><circle cx="1150" cy="91" r="4" fill="#f5e8c8"/>
<path d="M0 350Q150 331 300 350T600 350T900 350T1200 350T1500 350V720H0Z" fill="url(#ocean)"/>
<path d="M0 414q80-20 160 0t160 0t160 0t160 0t160 0t160 0t160 0t160 0t160 0" fill="none" stroke="#7291a0" stroke-width="5" opacity=".8"/>
<path d="M0 495q70-17 140 0t140 0t140 0t140 0t140 0t140 0t140 0t140 0t140 0t140 0" fill="none" stroke="#57788a" stroke-width="4"/>
<path d="M0 602q90-13 180 0t180 0t180 0t180 0t180 0t180 0t180 0" fill="none" stroke="#3d6177" stroke-width="4"/>
<path d="M812 456l244 0-44 48-157 0Z" fill="url(#hull)" stroke="#d0a56d" stroke-width="5"/>
<path d="M923 453V257M1018 456V299" stroke="#211e28" stroke-width="9"/>
<path d="M915 278L830 430H915ZM931 291L1004 424H931Z" fill="#d9d2bc" opacity=".87"/>
<path d="M1011 314l-68 108h68Z" fill="#b7c0bc" opacity=".8"/>
<path d="M832 462h208" stroke="#f2d491" stroke-width="4"/>
<circle cx="893" cy="484" r="5" fill="#f6d27c"/><circle cx="1020" cy="485" r="5" fill="#f6d27c"/>
<path d="M1083 512q40-22 80 0t80 0" fill="none" stroke="#b6a47e" stroke-width="3" opacity=".55"/>
<path d="M0 692H1280" stroke="#8e9e9d" stroke-width="3" opacity=".45"/>
</svg>''',
"dawn-sky.svg": '''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<defs>
 <linearGradient id="dawn" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#493f68"/><stop offset=".42" stop-color="#b46b82"/><stop offset=".78" stop-color="#f3a66c"/><stop offset="1" stop-color="#f6d28d"/></linearGradient>
 <radialGradient id="sunrise"><stop stop-color="#fff0b0" stop-opacity=".95"/><stop offset=".35" stop-color="#ffcf83" stop-opacity=".45"/><stop offset="1" stop-color="#ffb77b" stop-opacity="0"/></radialGradient>
 <linearGradient id="dawnSea" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#596881"/><stop offset="1" stop-color="#252e48"/></linearGradient>
</defs>
<rect width="1280" height="720" fill="url(#dawn)"/>
<ellipse cx="675" cy="444" rx="410" ry="285" fill="url(#sunrise)"/>
<circle cx="675" cy="463" r="83" fill="#ffe4a0"/>
<path d="M0 427Q170 390 340 426T680 425T1020 425T1360 425V720H0Z" fill="url(#dawnSea)"/>
<path d="M0 493q80-19 160 0t160 0t160 0t160 0t160 0t160 0t160 0t160 0t160 0" fill="none" stroke="#e5b98b" stroke-width="6" opacity=".8"/>
<path d="M0 564q75-14 150 0t150 0t150 0t150 0t150 0t150 0t150 0t150 0t150 0" fill="none" stroke="#8592a2" stroke-width="4" opacity=".7"/>
<path d="M0 644q90-18 180 0t180 0t180 0t180 0t180 0t180 0t180 0" fill="none" stroke="#59677d" stroke-width="4"/>
<path d="M103 184q52-54 103 0 37-43 78 0 67-47 129 0" fill="none" stroke="#c4a1a4" stroke-width="14" stroke-linecap="round" opacity=".7"/>
<path d="M796 239q50-45 95 0 33-42 77-2 45-53 94 4" fill="none" stroke="#d39c95" stroke-width="12" stroke-linecap="round" opacity=".72"/>
<path d="M388 302q38-32 76 0 29-29 62 0" fill="none" stroke="#cf9a99" stroke-width="9" stroke-linecap="round" opacity=".62"/>
<path d="M0 406H1280" stroke="#ffdca0" stroke-width="3" opacity=".66"/>
<path d="M572 523h206M607 548h138M630 574h90" stroke="#fff0b6" stroke-width="5" opacity=".45"/>
<path d="M1080 0H1280V720H1080Z" fill="#322f4a" opacity=".1"/>
</svg>'''
}

for name, svg in svgs.items():
    (SETS / name).write_text(svg + "\n", encoding="utf-8")

(PROPS / "beacon-lantern.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1100" viewBox="0 0 900 1100">
<defs><linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#3b4b55"/><stop offset="1" stop-color="#121e2b"/></linearGradient><radialGradient id="fire"><stop stop-color="#fff8cc"/><stop offset=".4" stop-color="#ffd36e"/><stop offset="1" stop-color="#f6a94e" stop-opacity=".15"/></radialGradient></defs>
<g transform="translate(330 400)">
<ellipse cx="120" cy="145" rx="112" ry="135" fill="url(#fire)" opacity=".65"/>
<path d="M74 48h92l-9-27H83Z" fill="#b88b55" stroke="#27323d" stroke-width="8"/>
<rect x="66" y="52" width="108" height="183" rx="19" fill="url(#metal)" stroke="#e1b96f" stroke-width="9"/>
<rect x="82" y="71" width="76" height="144" rx="12" fill="url(#fire)" stroke="#78858a" stroke-width="5"/>
<path d="M74 93h92M74 191h92M55 235h130M81 253h78" stroke="#d4aa68" stroke-width="9"/>
<path d="M90 253l-12 27h84l-12-27" fill="#374854" stroke="#202b36" stroke-width="7"/>
<path d="M110 185q-21-35 10-67 29 38 10 67Z" fill="#fff0ad"/>
</g>
</svg>\n''', encoding="utf-8")
(PROPS / "red-scarf.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="100" viewBox="0 0 300 100">
<defs><linearGradient id="cloth" x1="0" y1="0" x2="0.8" y2="1"><stop stop-color="#ed6558"/><stop offset="1" stop-color="#a62f3d"/></linearGradient></defs>
<!-- Compact central cloth shape: prop SVGs are otherwise drawn at 30% of canvas height. -->
<path d="M146 47Q150 46 154 47L153 50Q150 49 147 51Z" fill="url(#cloth)" stroke="#722b36" stroke-width="1.2"/>
<path d="M152 50l3 1-1 5-3-2Z" fill="url(#cloth)" stroke="#722b36" stroke-width="1"/>
<path d="M147 48q3 1 6 0" fill="none" stroke="#ffb099" stroke-width=".8" opacity=".65"/>
</svg>\n''', encoding="utf-8")
print(f"Generated {len(svgs)} backgrounds and 2 props under {ROOT}")
