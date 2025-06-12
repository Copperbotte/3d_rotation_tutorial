# Joseph Kessler
# 2025 June 9
# 3d_rotation_tutorial.py
################################################################################
#     This script builds the given markdown file with functional tables, as
# opposed to the expected human readable .md file.

import subprocess as sp
# Prints a line ran through a subprocess how you expect it to work!
def Call(command, getlines=False, silence=False):
    pprint = "> %s"%command
    print(pprint)
    lines = []
    with sp.Popen(command,
        stdout=sp.PIPE, stderr=sp.STDOUT,
        shell=True, universal_newlines=True # universal newlines makes it not a binary output
    ) as proc:
        for line in iter(proc.stdout.readline, ""):
            if not silence:
                print(line[:-1])
            if getlines:
                lines.append(line[:-1])
            
    if getlines:
        return proc.returncode, lines
    return proc.returncode

# from pathlib import Path
# import json
# jscache_path = './tex_cache/cache.json'
# jscache = dict()
# if Path.exists(jscache_path):
#     with open(jscache, 'r') as o:
#         jscache = json.load(o)

global SVG_FROM_TEX_PROCESSED
SVG_FROM_TEX_PROCESSED = 0
def SVG_FROM_TEX(TEX_INPUT, scale=1.25, inline=False, nodiv=False):
    global SVG_FROM_TEX_PROCESSED # weird python edge case. This doesn't scale, i'm not gonna sweat about it.
    TEX_TEMPLATE = r"""\documentclass[preview]{standalone}
\usepackage{xcolor}
\usepackage{amsmath}
\begin{document}

%s

\end{document}
"""

    # # Clean TEX_INPUT for use with the template above
    # TEX_INPUT = TEX_INPUT.replace('$$\n', r'\\' + '\n')
    # # Only $$ that exist are at the beginnings now or are with invalid lines
    # TEX_INPUT = TEX_INPUT.split('$$')
    TEX_INPUT = TEX_INPUT.split('\n')
    TEX_INPUT = [line.strip() for line in TEX_INPUT]
    TEX_INPUT = list(filter(None, TEX_INPUT))
    TEX_INPUT = '\n'.join(TEX_INPUT)
    TEX_OUTPUT = TEX_TEMPLATE%TEX_INPUT

    FONT_SIZE_MAGIC_NUMBER = 9.9626 #px, Found by extracting using cmd4.
    inkscape = r"C:\Program Files\Inkscape\bin\inkscape.exe"
    tex = "./tex_cache/render_%04d.tex"%SVG_FROM_TEX_PROCESSED
    pdf = tex.replace('.tex','.pdf')
    svg_tmp = tex.replace('.tex','_tmp.svg')
    #svg_tmp2 = tex.replace('.tex','_tmp2.svg')
    svg = tex.replace('.tex','.svg')
    fld = "./tex_cache"
    cmd1 = "pdflatex -output-directory=\"%s\" -interaction=nonstopmode \"%s\""%(fld, tex)
    cmd2 = "pdf2svg \"%s\" \"%s\""%(pdf, svg_tmp)
    cmd3 = "\"%s\" \"%s\" --export-type=svg --export-filename=\"%s\" --export-area-drawing"%(inkscape, svg_tmp, svg)
    #cmd4 = "\"%s\" \"%s\" --export-type=svg --export-filename=\"%s\" --export-text-to-path"%(inkscape, pdf, svg_tmp2)

    with open(tex, 'w') as o:
        o.write(TEX_OUTPUT)
    
    if False:

        if False:
            Call(cmd1, silence=True)
            print('#'*80)
            Call(cmd2, silence=True)
            print('#'*80)
        Call(cmd3, silence=True)
        #print('#'*80)
        #Call(cmd4, silence=True)

        # Postprocess SVG
        # Swap width to width="100%", and height to height="100%"
        with open(svg, 'r') as o:
            svg_text = o.read()

        replacements = [
            #["width=\"", 'width="100%"'],
            #["width=\"", 'width="10em"'],
            ["width=\"", ''],
            ["height=\"", 'height="100%"']
            #["height=\"", 'height="18.293624em"']
            #["height=\"", '']
        ]
        for k,v in replacements:
            i0 = svg_text.index(k)
            i1 = svg_text.index("\"", i0+1)+1
            i2 = svg_text.index("\"", i1)+1
            # svg_text[i0:i2] == 'width="153.40298"'
            if 'height' in k:
                height_px = svg_text[i1:i2-1]
                height_em = float(height_px)/FONT_SIZE_MAGIC_NUMBER
                height_em = height_em*scale
                v = 'height="%.6fem"'%height_em
            svg_text = svg_text[:i0] + v + svg_text[i2:]

        # Inject preserveAspectRatio="xMidYMid meet" into the svg tag
        svg_lines = svg_text.split('\n')
        ind = 0
        key = "viewBox"
        for n in range(len(svg_lines)):
            line = svg_lines[n].strip()
            if key in line:
                ind = n
                break
        svg_lines = svg_lines[:ind+1] + svg_lines[ind:]
        line = svg_lines[ind+1]
        svg_lines[ind+1] = line.split(key)[0] + 'preserveAspectRatio="xMidYMid meet"'
        svg_text = '\n'.join(svg_lines)

        # #3 and #4 is code written by ChatGPT.
        # 3. Replace hard-coded black fills with currentColor (if any)
        import re
        svg_text = re.sub(r'fill="#000000"|fill="#000"|fill="black"', 'fill="currentColor"', svg_text, flags=re.IGNORECASE)

        # 4. Inject dark mode CSS
        style_block = """
    <style>
        @media (prefers-color-scheme: dark)
        {
        svg {
            color: white;
        }
        }
    </style>"""
        # Insert just after opening <svg> tag
        ind = svg_text.index("<svg")
        ind = svg_text.index(">", ind+1)
        svg_text = svg_text[:ind+1] + style_block + svg_text[ind+1:]

        with open(svg, 'w') as o:
            o.write(svg_text)

    SVG_FROM_TEX_PROCESSED = SVG_FROM_TEX_PROCESSED + 1

    # The style applied here forces the svgs to stay inline with the text.
    if inline:
        #return f' ![{svg}]({svg}) '
        #return f'<img src="{svg}" style="vertical-align: middle; display: inline-block;"/>'
        #return f'<img src="{svg}" style="height=1em; vertical-align: -1.5em; display: inline-block;"/>'
        return f' <img src="{svg}" style="display: inline-block;"/> '
        result = f"""<div style="display: inline-block;"> 

<img src="{svg}"/>

</div>"""
        return result
        
    #result = f'<img src="{svg}"/>'
    result = """<div align="center"> 

%s

</div>"""
    
    #result = f'<div style="display: flex; align-items: center; justify-content: center; height: 100%; width: 100%;">{result}</div>'

    result = result%(f'![{svg}]({svg})')
    if nodiv:
        result = f'![{svg}]({svg})'
    return result

dst = "./3d_rotation_tutorial.md"

# This function supplies definitions for various latex helpers.
def MATHSUB(math):
    ############################################################################
    #     This should be done by regex, but regex is awful to understand.  Any 
    # benefits it yields far outweighs how difficult it is to read.  Is this a 
    # skill issue? perhaps, but ChatGPT exists, can translate regex for me, and
    # can write decent parsers.  I see no need to continue using it unless 
    # performance is critical. If a codebase requires use of an LLM to
    # understand, then its unmaintanable.
    # ChatGPT wrote the code below.  
    #
    # def replace_command(pattern, replacement, text):
    #     # Replace #1 in replacement with the matched group
    #     def repl(m):
    #         inner = m.group(1)
    #         return replacement.replace("#1", inner)
    #     # Pattern: match command name, then balanced braces
    #     # e.g. \\pwrap{...}
    #     regex = re.compile(rf"{pattern[:-4]}\{{((?:[^{{}}]+|{{(?:[^{{}}]+|{{[^{{}}]*}})*}})*?)\}}")
    #     return regex.sub(repl, text)
    # 
    # for pattern, replacement in commands.items():
    #     math = replace_command(pattern, replacement, math)
    # return math

    commands = {
        r"\pwrap{#1}": r"\left(#1\right)",
        r"\bwrap{#1}": r"\left[#1\right]",
        r"\mat{#1}" : r"\begin{bmatrix}#1\end{bmatrix}",
        r"\colorX{#1}" : r"\textcolor{red}{#1}", # #FF0000
        r"\colorY{#1}" : r"\textcolor{green}{#1}", # #00FF00
        r"\colorZ{#1}" : r"\textcolor{cyan}{#1}", # #007FFF
        r"\colorU{#1}" : r"\textcolor{magenta}{#1}", # #00FF7F
        r"\colorV{#1}" : r"\textcolor{orange}{#1}", # #FF00FF
        r"\colorW{#1}" : r"\textcolor{yellow}{#1}", # #FFFF00
    }

    def bs_fltr(s):
        keys = [r'\\', r'\{', r'\}']
        for key in keys:
            if key in s:
                s = s.replace(key, '~~')
        return s
    
    # If the command is malformed, this will crash
    cmd_bs_fltr = {k:k[:bs_fltr(k).index('{')] for k in commands.keys()}

    while True:
        # Swap sneaky edge sases with an equivelant number of irrelevant characters for indexing
        math_bs_fltr = bs_fltr(math)
        replacable = {k:cmd_bs_fltr[k] in math_bs_fltr for k,v in commands.items()}
        if not any(replacable.values()):
            return math

        for cmd in commands.keys():
            if not replacable[cmd]:
                continue
            
            # Find the first valid { from this command
            icmd0 = math_bs_fltr.index(cmd_bs_fltr[cmd])
            icmd1 = math_bs_fltr.index("{", icmd0) + 1
            # Find its pair }
            icmd2 = len(math_bs_fltr)
            braces = 1
            for n in range(icmd1, icmd2):
                if math_bs_fltr[n] == '{':
                    braces += 1
                if math_bs_fltr[n] == '}':
                    braces -= 1
                    if braces == 0:
                        icmd2 = n
                        break
            math = math[:icmd0] + commands[cmd].replace('#1', math[icmd1:icmd2]) + math[icmd2+1:]
            break

def MULTILINE(multiline_string):
    return multiline_string.strip()

def LANGUAGE_TABLE(math="", cpp="", csharp="", python=""):

    math = SVG_FROM_TEX(MATHSUB(math), scale=1.25)

    return MULTILINE(r"""
<table align="center">
<tr><td>Mathematics</td> <td>C#</td></tr>
<tr>
<td>

%s

</td>
<td>

```csharp
%s
```

</td>
</tr>
<tr><td></td><td></td></tr>
<tr><td>Python</td> <td>C++</td></tr>
<tr>
<td>

```py
%s
```

</td>
<td>

```cpp
%s
```

</td>
</tr>
</table>
"""%(math, csharp, python, cpp)) + '\n\n'

text = ""

text += MULTILINE("""
This is a tutorial written by Joe Kessler (@copperbotte, or @copper_irl) on 2025 April 12.

This tutorial builds toward an efficient way to rotating objects in 3d space.

# Linear Algebra & basis vectors

Before we start, first we'll have to go over some simple linear algebra.  It wont be too much, dont worry!  It may appear like a lot if you see the scroll bar, but there's a lot of fluff.  I'll present most concepts in 4 languages: Mathematics, C++, C#, and Python, respectively.  

## Linear Transforms
Given some function `func(arg)`
""")

text += LANGUAGE_TABLE(
    math=r"$$func(arg)$$",
    cpp=MULTILINE("""
template class<T>
T func(T arg);
"""),
    csharp="public T func<T>(T arg);",
    python=MULTILINE("""
def func(arg):
    ...
""")
)

text += MULTILINE(r"""
`func(arg)` is "Linear" if for inputs `T x` and `T y`, and for a float `s`:
""")

text += LANGUAGE_TABLE(
    math=MULTILINE(r"""
$$func(x\cdot s) = func(x)\cdot s$$
$$func(x + y) = func(x) + func(y)$$
"""),
    cpp=MULTILINE("""
float s;
T x, y;

Assert(func(x*s) == func(x)*s);
Assert(func(x + y) == func(x) + func(y));
"""),
    csharp=MULTILINE("""
float s;
T x, y;

Assert(func(x*s) == func(x)*s);
Assert(func(x + y) == func(x) + func(y));
"""),
    python=MULTILINE("""
assert func(x*s) == func(x)*s
assert func(x + y) == func(x) + func(y)
""")
)

text += MULTILINE("""
For example, lets look at coordinates like a `Vector3`.  It has three inputs rather than one, but we can interpret the resulting *object* as a function to check for linearity.
""")

text += LANGUAGE_TABLE(
    math=MULTILINE(r"""
$$\begin{align*}\text{Row Vectors}\end{align*}$$
$$\bwrap{x\cdot s,y\cdot s,z\cdot s} = \bwrap{x,y,z}\cdot s$$
$$\bwrap{x, y, z} = \bwrap{x,0,0} + \bwrap{0,y,0} + \bwrap{0,0,z}$$
$$\begin{align*}\text{Column Vectors}\end{align*}$$
$$\mat{x\cdot s\\y\cdot s\\z\cdot s} = \mat{x\\y\\z}\cdot s$$
$$\mat{x\\y\\z} = \mat{x\\0\\0} + \mat{0\\y\\0} + \mat{0\\0\\z}$$
"""),
    cpp=MULTILINE("""
float x, y, z, s;

// Note: XMFLOAT3s can't actually do this natively!
Assert(XMFLOAT3(x*s, y*s, z*s) == XMFLOAT3(x,y,z)*s);
Assert(
    XMFLOAT3(x,y,z) ==
    XMFLOAT3(x,0,0) +
    XMFLOAT3(0,y,0) + 
    XMFLOAT3(0,0,z)
);
"""),
    csharp=MULTILINE("""
float x, y, z, s;

Assert(new Vector3(x*s, y*s, z*s) == new Vector3(x,y,z)*s);
Assert(
    new Vector3(x,y,z) == 
    new Vector3(x,0,0) + 
    new Vector3(0,y,0) + 
    new Vector3(0,0,z)
);
"""),
    python=MULTILINE("""
vec = lambda *args: np.array([*args], dtype=np.float64)
All = np.all

assert All(vec(x*s, y*s, z*s) == vec(x,y,z)*s)
assert All(
    vec(x,y,z) == 
    vec(x,0,0) + 
    vec(0,y,0) + 
    vec(0,0,z)
)
""")
)

text += MULTILINE("""
This isn't enough to prove that these are *linear objects*, but it is enough to prove that these objects are *linear maps!*  This has an interesting consequence: The object we often use for affine transformations, `Vector4(x, y, z, 1);` is *not* linear, because multiplying by a float `s` or adding two of them together changes that 1 at the end, which we don't want.  However, the `x, y, z` within is, so you've gotta be careful when handling these.
""")
text += LANGUAGE_TABLE(
    math=MULTILINE(#r"""
#$$\begin{align*}\text{Row Vectors}\end{align*}$$
#$$\bwrap{x,y,z,1}\cdot s = \bwrap{x\cdot s,y\cdot s,z\cdot s,\textcolor{orange}{s}}$$
#$$\bwrap{x, y, z, 1} + \bwrap{u, v, w, 1} = \bwrap{x+u, y+v, z+w, \textcolor{orange}{2}}$$
#$$\begin{align*}\text{Column Vectors}\end{align*}$$
r"""
$$\mat{x\\y\\z\\1}\cdot s = \mat{x\cdot s\\y\cdot s\\z\cdot s\\\textcolor{orange}{s}}$$
$$\mat{x\\y\\z\\1} + \mat{u\\v\\w\\1} = \mat{x+u\\y+v\\z+w\\\textcolor{orange}{2}}$$
"""),
    cpp=MULTILINE("""
float x, y, z, s;

// Note: XMFLOAT4s can't actually do this natively!
// Note: Both of these assertions will fail.
Assert(XMFLOAT4(x,y,z,1)*s == XMFLOAT4(x*s,y*s,z*s,1));
Assert(
    XMFLOAT4(x,y,z,1) == 
    XMFLOAT4(x,0,0,1) + 
    XMFLOAT4(0,y,0,1) + 
    XMFLOAT4(0,0,z,1)
);
"""),
    csharp=MULTILINE("""
float x, y, z, s;

// Note: Both of these assertions will fail.
Assert(new Vector4(x,y,z,1)*s == new Vector4(x*s,y*s,z*s,1));
Assert(
    new Vector4(x,y,z,1) == 
    new Vector4(x,0,0,1) + 
    new Vector4(0,y,0,1) + 
    new Vector4(0,0,z,1)
);
"""),
    python=MULTILINE("""
vec = lambda *args: np.array([*args], dtype=np.float64)
All = np.all

# Note: Both of these assertions will fail.
assert All(vec(x,y,z,1)*s == vec(x*s,y*s,z*s,1))
assert All(
    vec(x,y,z,1) == 
    vec(x,0,0,1) + 
    vec(0,y,0,1) + 
    vec(0,0,z,1)
)
""")
)

################################################################################
text += MULTILINE("""
## Basis Vectors

There's another interesting consequence of these linear maps that very quickly lead to rotations.  Lets take another look at the following property:
""")
text += LANGUAGE_TABLE(
    math=MULTILINE(r"""
$$\mat{x\\y\\z} = \mat{x\\0\\0} + \mat{0\\y\\0} + \mat{0\\0\\z}$$
"""),
    cpp=MULTILINE("""
float x, y, z;

Assert(
    XMFLOAT3(x,y,z) == 
    XMFLOAT3(x,0,0) + 
    XMFLOAT3(0,y,0) + 
    XMFLOAT3(0,0,z)
);
"""),
    csharp=MULTILINE("""
float x, y, z;

Assert(
    new Vector3(x,y,z) == 
    new Vector3(x,0,0) + 
    new Vector3(0,y,0) + 
    new Vector3(0,0,z)
);
"""),
    python=MULTILINE("""
vec = lambda *args: np.array([*args], dtype=np.float64)
All = np.all

assert All(
    vec(x,y,z) == 
    vec(x,0,0) + 
    vec(0,y,0) + 
    vec(0,0,z)
)
""")
)
text += MULTILINE("""
That variable, `x`, is a float, and since all the other entries are 0, we can use the first property to commute `x` outside the vector!
""")
text += LANGUAGE_TABLE(
    math=MULTILINE(r"""
$$\mat{x\\0\\0} = \mat{1\\0\\0} x$$
"""),
    cpp=MULTILINE("""
float x, y, z;

Assert(XMFLOAT3(x,0,0) == XMFLOAT3(1,0,0)*x);
"""),
    csharp=MULTILINE("""
float x, y, z;

Assert(new Vector3(x,0,0) == new Vector3(1,0,0)*x);
"""),
    python=MULTILINE("""
vec = lambda *args: np.array([*args], dtype=np.float64)
All = np.all

assert All(vec(x,0,0) == vec(1,0,0)*x)
""")
)

text += MULTILINE("""
in general we can apply this to all three variables in a vector to find this:
""")
text += LANGUAGE_TABLE(
    math=MULTILINE(r"""
$$\mat{x\\y\\z} = \mat{1\\0\\0} x + \mat{0\\1\\0} y + \mat{0\\0\\1} z$$
"""),
    cpp=MULTILINE("""
float x, y, z;

Assert(
    XMFLOAT3(x,y,z) == 
    XMFLOAT3(1,0,0)*x + 
    XMFLOAT3(0,1,0)*y + 
    XMFLOAT3(0,0,1)*z
);
"""),
    csharp=MULTILINE("""
float x, y, z;

Assert(
    new Vector3(x,y,z) == 
    new Vector3(1,0,0)*x + 
    new Vector3(0,1,0)*y + 
    new Vector3(0,0,1)*z
);
"""),
    python=MULTILINE("""
vec = lambda *args: np.array([*args], dtype=np.float64)
All = np.all

assert All(
    vec(x,y,z) ==
    vec(1,0,0)*x + 
    vec(0,1,0)*y + 
    vec(0,0,1)*z
)
""")
)

text += MULTILINE("""
<div align="center">
<img src=basis.png height="256px"/>

[Source: Wikipedia.org (Retrieved 2025 July 09)](https://commons.wikimedia.org/wiki/File:3D_Vector.svg)
</div>

Those *constant* objects are the "standard" basis vectors for Euclidean space, which represent the directions each variable grows in.  They're the gizmos you'll see in 3d editors!  They're usually represented mathematically with a """ + SVG_FROM_TEX(MATHSUB(r"$\hat{\text{hat}}$"), scale=1, inline=True) + """ notation:
""")
text += LANGUAGE_TABLE(
    math=MULTILINE(r"""
$$\vec{X} = \mat{x\\y\\z} = \colorX{\mat{1\\0\\0}} x + \colorY{\mat{0\\1\\0}} y + \colorZ{\mat{0\\0\\1}} z$$
$$\vec{X} = \colorX{\hat{x}}\cdot x + \colorY{\hat{y}}\cdot y + \colorZ{\hat{z}}\cdot z$$
"""),
    cpp=MULTILINE("""
float x, y, z;
XMFLOAT3    X(x,y,z);
XMFLOAT3 xHat(1,0,0);
XMFLOAT3 yHat(0,1,0);
XMFLOAT3 zHat(0,0,1);

Assert(X == xHat*x + yHat*y + zHat*z);
"""),
    csharp=MULTILINE("""
float x, y, z;
Vector3 X    = new Vector3(x,y,z);
Vector3 xHat = new Vector3(1,0,0);
Vector3 yHat = new Vector3(0,1,0);
Vector3 zHat = new Vector3(0,0,1);

Assert(X == xHat*x + yHat*y + zHat*z);
"""),
    python=MULTILINE("""
vec = lambda *args: np.array([*args], dtype=np.float64)
All = np.all

X    = vec(x,y,z)
xHat = vec(1,0,0)
yHat = vec(0,1,0)
zHat = vec(0,0,1)

assert All(X == xHat*x + yHat*y + zHat*z)
""")
)

text += MULTILINE("""
If you're familiar with shaders, you've likely come across the dot product.  Take a look at the last line in every language above, they're *all dot products!* Usually people forgo the basis vectors and just focus on the column vectors.  When your source and destination are in the same coordinate system this is fine, but rotations *explicitly change them.*
""")
text += LANGUAGE_TABLE(
    math=MULTILINE(r"""
$$\vec{X} = \colorX{\hat{x}}\cdot x + \colorY{\hat{y}}\cdot y + \colorZ{\hat{z}}\cdot z$$
$$\vec{X} = \mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{\colorX{x}\\\colorY{y}\\\colorZ{z}}$$
"""),
    cpp=MULTILINE
   ("""
float x, y, z;
XMFLOAT3    X(x,y,z);
XMFLOAT3 xHat(1,0,0);
XMFLOAT3 yHat(0,1,0);
XMFLOAT3 zHat(0,0,1);
XMFLOAT3 Basis[3] = {xHat, yHat, zHat};

template <class B, class C>
B dot3(B* basis, C coord)
{
    B result = basis[0] * 0.0;
    for(int n=0; n<3; ++n)
        result += basis[n] * coord[n];
    return result;
}

Assert(xHat*x + yHat*y + zHat*z == dot3(Basis, X));
"""),
    csharp=MULTILINE("""
float x, y, z;
Vector3 X    = new Vector3(x,y,z);
Vector3 xHat = new Vector3(1,0,0);
Vector3 yHat = new Vector3(0,1,0);
Vector3 zHat = new Vector3(0,0,1);
Vector3 Basis = {xHat, yHat, zHat};

Vector3 dot3(Vector3[] basis, Vector3 coord)
{
    Vector3 result = Vector3.Zero;
    for(int n=0; n<3; ++n)
        result += basis[n] * coord[n];
    return result;
}
                     
Assert(xHat*x + yHat*y + zHat*z = dot3(Basis, X));
"""),
    python=MULTILINE("""
vec = lambda *args: np.array([*args], dtype=np.float64)
All = np.all

X    = vec(x,y,z)
xHat = vec(1,0,0)
yHat = vec(0,1,0)
zHat = vec(0,0,1)
Basis = vec(xHat, yHat, zHat)

def dot3(basis, coord):
    result = basis[0] * 0.0
    for n in range(3):
        result += basis[n] * coord[n]
    return result

assert All(xHat*x + yHat*y + zHat*z == dot3(Basis, X))
""")
)

text += MULTILINE("""
That choice of basis using the standard unit basis `[1,0,0], [0,1,0], [0,0,1]` is *arbitrary*, and as long as we use three unique, nonzero vectors that aren't scaled copies of each other, we can use whatever vectors we want as our basis!
""")

text += SVG_FROM_TEX(MATHSUB(r"""

$$\vec{X} = \colorU{\hat{u}\cdot a} + \colorV{\hat{v}\cdot b} + \colorW{\hat{w}\cdot c}$$

"""))

# $$\vec{X} = \mat{\colorU{\hat{u}}&\colorV{\hat{v}}&\colorW{\hat{w}}}\mat{\colorU{u}\\\colorV{v}\\\colorW{w}}$$

text += MULTILINE("""
(Please excuse only having math notation here, I'm at a loss of how to show this with code without skipping to the end)

Now here's the kicker: Those new basis vectors are *still vectors,* so they're linear, so we can decompose them in terms of that standard basis `[1,0,0], [0,1,0], [0,0,1]`:
""")

text += SVG_FROM_TEX(MATHSUB(r"""

$$\vec{X} = \pwrap{\colorU{\hat{u}}}\colorU{a} + \pwrap{\colorV{\hat{v}}}\colorV{b} + \pwrap{\colorW{\hat{w}}}\colorW{c}$$

$$\begin{align*}

    \colorU{\hat{u}} = \mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{\colorU{u}_{\colorX{x}}\\\colorU{u}_{\colorY{y}}\\\colorU{u}_{\colorZ{z}}}
&\quad&
    \colorV{\hat{v}} = \mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{\colorV{v}_{\colorX{x}}\\\colorV{v}_{\colorY{y}}\\\colorV{v}_{\colorZ{z}}}
&\quad&
    \colorW{\hat{w}} = \mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{\colorW{w}_{\colorX{x}}\\\colorW{w}_{\colorY{y}}\\\colorW{w}_{\colorZ{z}}}

\end{align*}$$

$$\vec{X} = 
    \pwrap{\mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{\colorU{u}_{\colorX{x}}\\\colorU{u}_{\colorY{y}}\\\colorU{u}_{\colorZ{z}}}}\colorU{a} + 

    \pwrap{\mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{\colorV{v}_{\colorX{x}}\\\colorV{v}_{\colorY{y}}\\\colorV{v}_{\colorZ{z}}}}\colorV{b} + 

    \pwrap{\mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{\colorW{w}_{\colorX{x}}\\\colorW{w}_{\colorY{y}}\\\colorW{w}_{\colorZ{z}}}}\colorW{c}$$

"""))

text += MULTILINE("""
Since the coordinate """ + SVG_FROM_TEX(MATHSUB(r"$\bwrap{\colorU{a}, \colorV{b}, \colorW{c}}$"), scale=1.0, inline=True) + """ are all floats, we can group them with the coordinates. And since all the basis vectors are the same, we can rearrange the terms of the dot products to find this:
""")

text += SVG_FROM_TEX(MATHSUB(r"""

$$\vec{X} = \mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\pwrap{
    \mat{\colorU{u}_{\colorX{x}}\\\colorU{u}_{\colorY{y}}\\\colorU{u}_{\colorZ{z}}}\colorU{a} + 
    \mat{\colorV{v}_{\colorX{x}}\\\colorV{v}_{\colorY{y}}\\\colorV{v}_{\colorZ{z}}}\colorV{b} + 
    \mat{\colorW{w}_{\colorX{x}}\\\colorW{w}_{\colorY{y}}\\\colorW{w}_{\colorZ{z}}}\colorW{c}
}$$

"""))

text += MULTILINE(MATHSUB("""
Notice how the resulting sum in the parenthesis is a coordinate! Despite this, it also has the characteristic form of a second dot product.  If we package it as such, with the coordinate """ + SVG_FROM_TEX(MATHSUB(r"$\bwrap{\colorU{a}, \colorV{b}, \colorW{c}}$"), scale=1.0, inline=True) + """ becoming a column vector like """  + SVG_FROM_TEX(MATHSUB(r"$\bwrap{\colorX{x}, \colorY{y}, \colorZ{z}}$"), scale=1.0, inline=True) + """ then we find the familiar face of a Matrix!
"""))

text += LANGUAGE_TABLE(
    math=MULTILINE(r"""
$$\vec{X} = \colorX{\hat{x}}\cdot \colorX{x} + \colorY{\hat{y}}\cdot \colorY{y} + \colorZ{\hat{z}}\cdot \colorZ{z}$$
$$\vec{X} = \mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{\colorX{x}\\\colorY{y}\\\colorZ{z}}$$
$$\mat{\colorX{x}\\\colorY{y}\\\colorZ{z}} = 
    \mat{\colorU{u}_{\colorX{x}}\\\colorU{u}_{\colorY{y}}\\\colorU{u}_{\colorZ{z}}}\colorU{a} + 
    \mat{\colorV{v}_{\colorX{x}}\\\colorV{v}_{\colorY{y}}\\\colorV{v}_{\colorZ{z}}}\colorV{b} + 
    \mat{\colorW{w}_{\colorX{x}}\\\colorW{w}_{\colorY{y}}\\\colorW{w}_{\colorZ{z}}}\colorW{c}$$
$$\mat{\colorX{x}\\\colorY{y}\\\colorZ{z}} = \mat{
    \mat{\colorU{u}_{\colorX{x}}\\\colorU{u}_{\colorY{y}}\\\colorU{u}_{\colorZ{z}}} &  
    \mat{\colorV{v}_{\colorX{x}}\\\colorV{v}_{\colorY{y}}\\\colorV{v}_{\colorZ{z}}} &
    \mat{\colorW{w}_{\colorX{x}}\\\colorW{w}_{\colorY{y}}\\\colorW{w}_{\colorZ{z}}}
}\mat{\colorU{a}\\\colorV{b}\\\colorW{c}}$$
$$\vec{X} = \mat{\colorX{\hat{x}}&\colorY{\hat{y}}&\colorZ{\hat{z}}}\mat{
    \colorU{u}_{\colorX{x}}&\colorV{v}_{\colorX{x}}&\colorW{w}_{\colorX{x}}\\
    \colorU{u}_{\colorY{y}}&\colorV{v}_{\colorY{y}}&\colorW{w}_{\colorY{y}}\\
    \colorU{u}_{\colorZ{z}}&\colorV{v}_{\colorZ{z}}&\colorW{w}_{\colorZ{z}}
}\mat{\colorU{a}\\\colorV{b}\\\colorW{c}}$$
"""),
    cpp=MULTILINE
   ("""
float a, b, c;
float ux, uy, uz;
float vx, vy, vz;
float wx, wy, wz;
XMFLOAT3  ABC( a, b, c);
XMFLOAT3 uHat(ux,uy,uz);
XMFLOAT3 vHat(vx,vy,vz);
XMFLOAT3 wHat(wx,wy,wz);
XMFLOAT3 Basis[3] = {uHat, vHat, wHat};

template <class B, class C>
B dot3(B* basis, C coord)
{
    B result = basis[0] * 0.0;
    for(int n=0; n<3; ++n)
        result += basis[n] * coord[n];
    return result;
}

XMFLOAT3 X = dot3(Basis, ABC);
"""),
    csharp=MULTILINE("""
float a, b, c;
float ux, uy, uz;
float vx, vy, vz;
float wx, wy, wz;
Vector3  ABC = new Vector3( a, b, c);
Vector3 uHat = new Vector3(ux,uy,uz);
Vector3 vHat = new Vector3(vx,vy,vz);
Vector3 wHat = new Vector3(wx,wy,wz);
Vector3 Basis = {uHat, vHat, wHat};

Vector3 dot3(Vector3[] basis, Vector3 coord)
{
    Vector3 result = Vector3.Zero;
    for(int n=0; n<3; ++n)
        result += basis[n] * coord[n];
    return result;
}
                     
Vector3 X = dot3(Basis, ABC);
"""),
    python=MULTILINE("""
vec = lambda *args: np.array([*args], dtype=np.float64)
All = np.all

ABC  = vec( a, b, c);
uHat = vec(ux,uy,uz);
vHat = vec(vx,vy,vz);
wHat = vec(wx,wy,wz);

Basis = vec(uHat, vHat, wHat)

def dot3(basis, coord):
    result = basis[0] * 0.0
    for n in range(3):
        result += basis[n] * coord[n]
    return result

X = dot3(Basis, ABC)
""")
)




################################################################################

with open(dst, 'w') as o:
    o.write(text)
