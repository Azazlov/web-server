"""
Build script: combines, minifies, and obfuscates static assets for production.
Reads from static/css/ and static/js/, writes obfuscated bundles to static/dist/.
"""
import os
import re
import json
import random
import string
import hashlib
import shutil

# Minification libraries
try:
    from rjsmin import jsmin
    HAS_JS_MIN = True
except ImportError:
    HAS_JS_MIN = False

try:
    from csscompressor import compress
    HAS_CSS_MIN = True
except ImportError:
    HAS_CSS_MIN = False

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, 'static')
DIST = os.path.join(STATIC, 'dist')

CSS_FILES = ['css/style.css']
JS_FILES = ['js/main.js']

# Seeds for obfuscation (randomized per build)
OBFUSCATION_SEED = ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def minify_css(css):
    """Minify CSS using csscompressor or fallback."""
    if HAS_CSS_MIN:
        return compress(css)
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
    return css.strip()


def obfuscate_css(css):
    """
    Obfuscate CSS by renaming class-like identifiers in a deterministic way.
    Only renames safe identifiers (our custom classes, not Bootstrap).
    """
    # Generate a short hash for class renaming
    class_map = {}

    def rename_custom_class(match):
        cls = match.group(1)
        # Don't rename Bootstrap/Bootstrap Icons classes
        if cls.startswith('bi-') or cls.startswith('modal') or cls.startswith('btn') or \
           cls.startswith('form') or cls.startswith('table') or cls.startswith('alert') or \
           cls.startswith('card') or cls.startswith('nav') or cls.startswith('dropdown') or \
           cls.startswith('toast') or cls.startswith('progress') or cls.startswith('badge') or \
           cls.startswith('breadcrumb') or cls.startswith('spinner') or cls.startswith('visually') or \
           cls.startswith('position') or cls.startswith('d-') or cls.startswith('text') or \
           cls.startswith('bg-') or cls.startswith('border') or cls.startswith('shadow') or \
           cls.startswith('overflow') or cls.startswith('w-') or cls.startswith('h-') or \
           cls.startswith('mh-') or cls.startswith('mv-') or cls.startswith('me-') or \
           cls.startswith('ms-') or cls.startswith('mt-') or cls.startswith('mb-') or \
           cls.startswith('p-') or cls.startswith('px') or cls.startswith('py') or \
           cls.startswith('g-') or cls.startswith('col') or cls.startswith('row') or \
           cls.startswith('align') or cls.startswith('justify') or cls.startswith('flex') or \
           cls.startswith('float') or cls.startswith('clearfix') or cls.startswith('sr') or \
           cls.startswith('img') or cls.startswith('figure') or cls.startswith('embed') or \
           cls.startswith('object') or cls.startswith('container') or cls.startswith('visible') or \
           cls.startswith('invisible') or cls.startswith('stretched') or cls.startswith('pe') or \
           cls.startswith('ps') or cls.startswith('lh') or cls.startswith('fw') or \
           cls.startswith('font') or cls.startswith('user') or cls.startswith('rounded') or \
           cls.startswith('opacity') or cls.startswith('hstack') or cls.startswith('vstack') or \
           cls.startswith('gap') or cls.startswith('placeholder') or cls.startswith('list') or \
           cls.startswith('ratio') or cls.startswith('offcanvas') or cls.startswith('scrollspy') or \
           cls.startswith('accordion') or cls.startswith('carousel') or cls.startswith('popover') or \
           cls.startswith('tooltip') or cls.startswith('close') or cls.startswith('modal-backdrop'):
            return match.group(0)
        if cls not in class_map:
            class_map[cls] = '_' + hashlib.md5((cls + OBFUSCATION_SEED).encode()).hexdigest()[:8]
        return '.' + class_map[cls]

    css = re.sub(r'\.([a-zA-Z_][a-zA-Z0-9_-]*)', rename_custom_class, css)
    return css


def obfuscate_js(js):
    """
    Obfuscate JavaScript code:
    1. Remove comments and debug statements
    2. Remove console statements
    3. Rename local function/variable names
    4. Add dead code injection
    5. Add anti-debug check
    """
    # Step 1: Remove all comments
    js = re.sub(r'//.*$', '', js, flags=re.MULTILINE)
    js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)

    # Step 2: Remove console statements
    js = re.sub(r'console\.(log|warn|error|info|debug|trace)\([^)]*\);?', '', js)

    # Step 3: Remove debugger statements
    js = re.sub(r'\bdebugger\b;?', '', js)

    # Step 4: Rename top-level function names
    function_name_map = {}
    func_counter = [0]

    def generate_obfuscated_name():
        func_counter[0] += 1
        chars = string.ascii_lowercase + string.ascii_uppercase
        return '_0x' + ''.join(random.choices(chars + string.digits, k=8))

    def rename_functions(js_code):
        # Function declarations
        pattern = r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('

        def replace_func(match):
            name = match.group(1)
            # Don't rename: functions called from HTML templates or Flask callbacks
            if name in ('initAlerts', 'initDeleteConfirmation', 'initFilePreview',
                        'initKeyboardShortcuts', 'initTooltips', 'initPopovers',
                        'initTableInteractions', 'initUploadProgress', 'initNavbarScroll',
                        'initAnimations', 'initRippleEffect', 'initDragDropUpload',
                        'initMobileSwipe', 'openPreview', 'openRenameModal', 'escapeHtml',
                        'renderMarkdown', 'showToast', 'formatFileSize', 'formatDate',
                        'scrollToElement', 'copyToClipboard', 'showConfirmDialog',
                        'preventDefaults', 'load_user', 'dirname_filter', 'inject_utils',
                        # Also keep: DOM event handlers referenced in HTML
                        ):
                return match.group(0)
            if name not in function_name_map:
                function_name_map[name] = generate_obfuscated_name()
            return f'function {function_name_map[name]}('

        js_code = re.sub(pattern, replace_func, js_code)

        # Function expressions: const/var/let name = function(...) {
        pattern2 = r'\b(const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\s*\('

        def replace_func2(match):
            keyword = match.group(1)
            name = match.group(2)
            if name.startswith('_') or name in function_name_map:
                return match.group(0)
            # Don't rename DOM callback names that might be used in HTML
            if name in ('onload', 'onerror', 'onclick', 'onchange', 'onsubmit',
                        'onkeydown', 'onkeyup', 'onfocus', 'onblur'):
                return match.group(0)
            if name not in function_name_map:
                function_name_map[name] = generate_obfuscated_name()
            return f'{keyword} {function_name_map[name]} = function('

        js_code = re.sub(pattern2, replace_func2, js_code)

        # Arrow function const declarations
        pattern3 = r'\b(const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\([^)]*\)\s*=>'

        def replace_func3(match):
            keyword = match.group(1)
            name = match.group(2)
            if name.startswith('_') or name in function_name_map:
                return match.group(0)
            if name not in function_name_map:
                function_name_map[name] = generate_obfuscated_name()
            return f'{keyword} {function_name_map[name]} = '

        js_code = re.sub(pattern3, replace_func3, js_code)

        # Arrow function with single param: const name = param => ...
        pattern4 = r'\b(const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=>'

        def replace_func4(match):
            keyword = match.group(1)
            name = match.group(2)
            param = match.group(3)
            if name.startswith('_') or name in function_name_map:
                return match.group(0)
            if name not in function_name_map:
                function_name_map[name] = generate_obfuscated_name()
            return f'{keyword} {function_name_map[name]} = {param} =>'

        js_code = re.sub(pattern4, replace_func4, js_code)

        return js_code

    js = rename_functions(js)

    # Step 5: Add dead code injection (random useless code blocks)
    dead_code = []
    for i in range(random.randint(3, 6)):
        var_name = '_0x' + ''.join(random.choices(string.ascii_lowercase, k=6))
        val = random.randint(1000, 9999)
        mult = random.randint(2, 9)
        dead_code.append(
            f'(function(){{var {var_name}={val};return {var_name}*{mult}+{random.randint(100,999)};}})();'
        )

    # Inject dead code at the beginning
    if dead_code:
        js = '(function(){' + ''.join(dead_code) + '})();\n' + js

    # Step 6: Add anti-debug check
    anti_debug = f'(function(){{var _s="{OBFUSCATION_SEED}";if(typeof window!=="undefined"&&window.outerHeight-window.innerHeight>200)return;}})();'
    js = anti_debug + '\n' + js

    # Step 7: Final minification pass
    if HAS_JS_MIN:
        js = jsmin(js)

    # Remove extra whitespace
    js = re.sub(r'\n{2,}', '\n', js)
    js = js.strip()

    return js


def minify_css_pipeline(css):
    """Full CSS pipeline: minify + obfuscate."""
    minified = minify_css(css)
    obfuscated = obfuscate_css(minified)
    return obfuscated


def minify_js_pipeline(js):
    """Full JS pipeline: minify + obfuscate."""
    minified = jsmin(js) if HAS_JS_MIN else js
    obfuscated = obfuscate_js(minified)
    return obfuscated


def build_bundle(file_list, pipeline, bundle_name, static_root):
    """Combine and process a list of files into a single bundle."""
    print(f"  Building {bundle_name}...")
    parts = []
    for rel_path in file_list:
        full_path = os.path.join(static_root, rel_path)
        if not os.path.exists(full_path):
            print(f"    WARNING: {rel_path} not found, skipping")
            continue
        content = read_file(full_path)
        parts.append(content)
        print(f"    + {rel_path} ({len(content):,} bytes)")

    combined = '\n'.join(parts)
    processed = pipeline(combined)

    original_size = len(combined.encode('utf-8'))
    final_size = len(processed.encode('utf-8'))
    ratio = (1 - final_size / original_size) * 100 if original_size else 0
    print(f"  {bundle_name}: {original_size:,} → {final_size:,} bytes ({ratio:.0f}% saved)")

    return processed


def build():
    """Run the full build with obfuscation."""
    print("Building static assets for production...")
    print(f"  Obfuscation seed: {OBFUSCATION_SEED}")
    print()

    # Clean dist directory
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    # Build CSS bundle
    css = build_bundle(CSS_FILES, minify_css_pipeline, 'style.min.css', STATIC)
    write_file(os.path.join(DIST, 'style.min.css'), css)

    # Build JS bundle
    js = build_bundle(JS_FILES, minify_js_pipeline, 'main.min.js', STATIC)
    write_file(os.path.join(DIST, 'main.min.js'), js)

    print()
    print(f"Build complete! Output in static/dist/")
    print(f"  Files are minified + obfuscated.")
    print(f"  Each build generates unique identifiers (seed: {OBFUSCATION_SEED}).")
    return True


if __name__ == '__main__':
    build()
