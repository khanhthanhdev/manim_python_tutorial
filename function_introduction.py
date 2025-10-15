from manim import *

from manim_ace.code import CodeWindow
from manim_ace.colors import (IBM_BLUE_60, IBM_RED_60, BLACK_19, TRUE_BACKGROUND_COLOR, FALSE_BACKGROUND_COLOR,
                              IBM_CYAN_60, IBM_MAGENTA_60, IBM_PURPLE_60,
                              SECONDARY_RECT_COLOR, IBM_GREEN_20,
                              IBM_BLUE_20, TOL_ORANGE)
from manim_ace.fonts import LM_MONO, ROBOTO_MONO
from manim_ace.functions import Function
from manim_ace.lists import List
from manim_ace.scene import AnimatedCodeScene, create_pc
from manim_ace.variables import VariableArea, code_value


class CodeSectionHelper:
    CODE_ANCHOR = [-6.5, 2.0, 0]
    VARIABLES_ANCHOR = [5.0, 2.0, 0]

    def __init__(self, scene: AnimatedCodeScene, title: str, code_text: str,
                 code_scale: float = 0.68, vars_per_row: int = 1):
        self.scene = scene
        self.title_text = title
        self.code_text = code_text
        self.code_scale = code_scale
        self.vars_per_row = vars_per_row
        self.annotations: list[Mobject] = []
        self.title: Mobject | None = None
        self.code: CodeWindow | None = None
        self.variables: VariableArea | None = None
        self._annotation_anchors: dict[str, Mobject] = {}
        self._base_z = 6

    def setup(self):
        self.scene.next_section(name=self.title_text)
        # Snapshot scene mobjects so we can remove anything this section adds
        # later in tear_down(). We store the actual object identities.
        self._initial_scene_mobjects = set(self.scene.mobjects)
    # Also snapshot any existing function visualizations so we don't
    # accidentally remove persistent library state later. We will
    # remove any functions added during this section.
        self._initial_functions = set(getattr(self.scene, 'functions', VGroup()).submobjects)
        # Snapshot current children of each layer so we can remove
        # mobjects added into existing layers (e.g., occluders) which
        # would not appear as top-level scene.mobjects.
        try:
            self._initial_layer_children = {i: set(layer.submobjects) for i, layer in enumerate(getattr(self.scene, 'layers', []))}
        except Exception:
            self._initial_layer_children = {}

        self.title = Text(self.title_text, font_size=42, font=ROBOTO_MONO, color=BLACK)
        self.title.to_edge(UP, buff=0.5)
        self.title.set_z_index(self._base_z + 4)
        self.scene.play(Write(self.title))

        self.code = CodeWindow(self.code_text, tab_width=4)
        self.code.scale(self.code_scale)
        self.code.align_to(self.CODE_ANCHOR, UL)
        self.code.set_opacity(0)
        self.code.set_z_index(self._base_z)
        self.scene.set_code(self.code)
        self.scene.play(FadeIn(self.code))
        self.scene.bring_to_front(self.code)
        self.code.set_opacity(1)
        for submob in self.code.submobjects:
            submob.set_z_index(self._base_z)
            submob.set_opacity(1)

        self.variables = VariableArea(vars_per_row=self.vars_per_row)
        self.variables.align_to(self.VARIABLES_ANCHOR, UR)
        self.variables.set_opacity(0)
        self.variables.set_z_index(self._base_z)
        self.scene.set_variables(self.variables)
        self.scene.play(FadeIn(self.variables))
        self.scene.bring_to_front(self.variables)
        self.variables.set_opacity(1)
        for submob in self.variables.submobjects:
            submob.set_z_index(self._base_z)
            submob.set_opacity(1)
        self._annotation_anchors = {
            'code': self.code,
            'variables': self.variables,
        }
        return self

    def add_annotation(self, mobj: Mobject, *, fade_in: bool = True,
                       auto_position: bool = False,
                       anchor: Mobject | None = None,
                       direction=DOWN, buff: float = 0.4,
                       column: str = 'code',
                       aligned_edge=LEFT):
        if auto_position:
            anchor = anchor or self._annotation_anchors.get(column) or self.code
            mobj.next_to(anchor, direction, buff=buff)
            if column == 'variables':
                mobj.align_to(self.variables, aligned_edge)
            else:
                mobj.align_to(self.code, aligned_edge)
            self._annotation_anchors[column] = mobj
        self.annotations.append(mobj)
        mobj.set_z_index(self._base_z + 3)
        if fade_in:
            self.scene.play(FadeIn(mobj))
        # Ensure annotations are visible above other elements
        self.scene.bring_to_front(mobj)
        return mobj

    def remove_annotation(self, mobj: Mobject):
        if mobj in self.annotations:
            self.annotations.remove(mobj)

    def highlight_lines(self, start: int, end: int, color, fill_opacity: float = 0.05,
                        stroke_width: float = 2):
        assert self.code is not None
        lines = self.code.lines(start, end)
        rect = SurroundingRectangle(lines, color=color, buff=0.12)
        rect.set_fill(color, fill_opacity)
        rect.set_stroke(color, width=stroke_width)
        rect.set_z_index(self._base_z - 1)
        self.annotations.append(rect)
        self.scene.play(Create(rect))
        self.scene.bring_to_front(self.code)
        for submob in self.code.submobjects:
            self.scene.bring_to_front(submob)
        return rect

    def highlight_tokens(self, tokens: Mobject, color, fill_opacity: float = 0.05,
                         stroke_width: float = 2):
        rect = SurroundingRectangle(tokens, color=color, buff=0.08)
        rect.set_fill(color, fill_opacity)
        rect.set_stroke(color, width=stroke_width)
        rect.set_z_index(self._base_z - 1)
        self.annotations.append(rect)
        self.scene.play(Create(rect))
        self.scene.bring_to_front(self.code)
        for submob in self.code.submobjects:
            self.scene.bring_to_front(submob)
        return rect

    def tear_down(self, *extra: Mobject):
        # Clear variables from the VariableArea first
        if self.variables:
            # Remove all variable boxes and their sub-elements from the scope
            for scope in self.variables.scope_stack:
                for var_name, var_box in list(scope.variable_boxes.items()):
                    if var_box in self.scene.mobjects:
                        # Remove the variable box and all its sub-mobjects
                        self.scene.remove(var_box)
                        for submob in var_box.submobjects:
                            if submob in self.scene.mobjects:
                                self.scene.remove(submob)
                scope.variable_boxes.clear()

            # Also remove any remaining sub-elements of the VariableArea recursively
            def remove_recursive(mobj):
                if mobj in self.scene.mobjects:
                    self.scene.remove(mobj)
                for sub in mobj.submobjects:
                    remove_recursive(sub)
            
            remove_recursive(self.variables)

        # Clear code window and all its sub-elements recursively
        if self.code:
            def remove_recursive(mobj):
                if mobj in self.scene.mobjects:
                    self.scene.remove(mobj)
                for sub in mobj.submobjects:
                    remove_recursive(sub)
            
            remove_recursive(self.code)

        # First, fade out everything
        fade_targets = []
        if self.title:
            fade_targets.append(self.title)
        if self.code:
            fade_targets.append(self.code)
        if self.variables:
            fade_targets.append(self.variables)
        fade_targets.extend(self.annotations)
        fade_targets.extend(extra)

        if fade_targets:
            self.scene.play(*[FadeOut(target) for target in fade_targets])

        # Then explicitly remove from scene
        for target in fade_targets:
            if target in self.scene.mobjects:
                self.scene.remove(target)

        # Clear scene references
        if getattr(self.scene, "code_window", None) is self.code:
            self.scene.code_window = None
        if getattr(self.scene, "variables", None) is self.variables:
            self.scene.variables = None
        if hasattr(self.scene, 'pc'):
            if self.scene.pc and self.scene.pc in self.scene.mobjects:
                self.scene.remove(self.scene.pc)
            self.scene.pc = None

        # Clear our references
        self.annotations.clear()
        self._annotation_anchors = {}
        self.title = None
        self.code = None
        self.variables = None

        # Remove any mobjects that were added to the scene during this
        # section (but keep persistent scene containers like layers and
        # the functions group). This catches copies or helper-created
        # objects that were not explicitly tracked.
        try:
            initial = getattr(self, '_initial_scene_mobjects', set())
            to_remove = []
            for m in list(self.scene.mobjects):
                if m in initial:
                    continue
                # Never remove the layers list/group or the functions VGroup
                if m is getattr(self.scene, 'functions', None):
                    continue
                if m is getattr(self.scene, 'layers', None):
                    continue
                # Also keep camera and other core attributes
                if m is getattr(self.scene, 'camera', None):
                    continue
                to_remove.append(m)
            if to_remove:
                # Use scene.remove which handles nested groups properly
                self.scene.remove(*to_remove)
            # Also remove any new children that were added into existing
            # layers (occluders, temporary overlays, etc.). Those are
            # nested inside layer groups, so remove any child not present
            # in the snapshot we captured at setup.
            try:
                initial_layers = getattr(self, '_initial_layer_children', {})
                for i, layer in enumerate(getattr(self.scene, 'layers', [])):
                    init_children = initial_layers.get(i, set())
                    # iterate copy since we'll remove
                    for child in list(layer.submobjects):
                        if child in init_children:
                            continue
                        # don't remove the functions container or the layers list itself
                        if child is getattr(self.scene, 'functions', None):
                            continue
                        # Remove via scene.remove so nested removal works
                        try:
                            self.scene.remove(child)
                        except Exception:
                            pass
            except Exception:
                pass
            # Also remove any function visuals that were added to the
            # scene.functions group during this section.
            try:
                initial_fn = getattr(self, '_initial_functions', set())
                new_fns = [f for f in list(getattr(self.scene, 'functions', VGroup()).submobjects) if f not in initial_fn]
                if new_fns:
                    # Remove them from the functions VGroup
                    for f in new_fns:
                        try:
                            self.scene.functions.remove(f)
                        except Exception:
                            # Fallback: call scene.remove to handle nested groups
                            self.scene.remove(f)
            except Exception:
                pass
        except Exception:
            pass


class NestedFunctionAnimator:
    CODE = """def outer_greeting(first, last):
    greeting = "Hi"
    def build_message():
        return f"{greeting}, {first} {last}"
    return build_message()

result = outer_greeting("Ali", "Baba")
print(result)"""

    def __init__(self, scene: AnimatedCodeScene):
        self.scene = scene

    def play(self):
        helper = CodeSectionHelper(self.scene, "Nested Functions", self.CODE,
                                   code_scale=0.67, vars_per_row=1).setup()

        summary = Text(
            "Functions defined inside other functions capture outer variables.",
            font_size=24, font=ROBOTO_MONO, color=BLACK
        )
        summary.to_corner(DL, buff=0.5)  # Bottom left corner to avoid overlap with right side
        helper.add_annotation(summary, auto_position=False)  # Manual positioning

        helper.highlight_lines(1, 5, IBM_BLUE_20)
        helper.highlight_lines(3, 4, IBM_PURPLE_60)
        
        # Ensure summary stays visible after highlights
        self.scene.bring_to_front(summary)

        closure_note = Text(
            "Inner function captures:\n"
            "greeting, first, last",
            font_size=20, font=ROBOTO_MONO, color=IBM_PURPLE_60
        )
        helper.add_annotation(closure_note, auto_position=True, buff=0.9, column='variables')

        self.scene.wait(0.5)
        self.scene.create_variable('greeting', 'Hi')
        # Set z_index for new variables and ensure annotations stay visible above new variables
        for scope in self.scene.variables.scope_stack:
            for var_box in scope.variable_boxes.values():
                var_box.set_z_index(6)
                for submob in var_box.submobjects:
                    submob.set_z_index(6)
        for annotation in helper.annotations:
            self.scene.bring_to_front(annotation)
        self.scene.wait(0.2)

        call_note = Text(
            "Calling outer_greeting\n"
            "returns nested result",
            font_size=20, font=ROBOTO_MONO, color=IBM_BLUE_60
        )
        helper.add_annotation(call_note, auto_position=True, buff=0.65, column='variables')

        self.scene.create_variable('result', 'Hi, Ali Baba!')
        # Ensure all variable boxes are visible above other elements
        for scope in self.scene.variables.scope_stack:
            for var_box in scope.variable_boxes.values():
                var_box.set_z_index(6)
                for submob in var_box.submobjects:
                    submob.set_z_index(6)
        # Ensure annotations stay visible above new variables
        for annotation in helper.annotations:
            self.scene.bring_to_front(annotation)
        self.scene.wait(1.0)

        helper.tear_down()


class DocstringAnimator:
    CODE = '''def describe_pet(name, age):
    """
    Return a friendly description of a pet.

    Args:
        name (str): Name of the pet
        age (int): Age in years
    """
    return f"{name} is {age} years old."

doc = describe_pet.__doc__
print(doc)'''

    def __init__(self, scene: AnimatedCodeScene):
        self.scene = scene

    def play(self):
        helper = CodeSectionHelper(self.scene, "Function Docstrings", self.CODE,
                                   code_scale=0.63).setup()

        # Move variables more to the left to fit the wide docstring box
        helper.variables.shift(LEFT)

        helper.highlight_lines(1, 8, IBM_CYAN_60)

        description = Text(
            "__doc__ keeps the documentation right on the function.",
            font_size=26, font=ROBOTO_MONO, color=IBM_CYAN_60
        )
        description.to_edge(DOWN, buff=0.5)
        description.move_to([0, description.get_y(), 0])  # Center horizontally
        helper.add_annotation(description, auto_position=False)  # Manual positioning

        # doc_preview = Text(
        #     "Return a friendly description of a pet.\n\n"
        #     "Args:\n"
        #     "    name (str): Name of the pet\n"
        #     "    age (int): Age in years",
        #     font_size=18, font=LM_MONO, color=BLACK, line_spacing=0.6
        # )
        # helper.add_annotation(doc_preview, auto_position=True, anchor=description, buff=0.3, column='variables')

        self.scene.wait(0.5)
        # Create variable with the actual docstring content
        docstring_content = (
            "Return a friendly description of a pet.\n\n"
            "Args:\n"
            "    name (str): Name of the pet\n"
            "    age (int): Age in years"
        )
        self.scene.create_variable('doc', docstring_content)
        # Ensure variable contents are above the box and annotations are on top
        for scope in self.scene.variables.scope_stack:
            for var_name, var_box in scope.variable_boxes.items():
                if var_name == 'doc':
                    var_box.set_z_index(6)
                    var_box['contents'].set_z_index(10)  # Contents above everything
                    self.scene.bring_to_front(var_box['contents'])
                else:
                    var_box.set_z_index(6)
                    for submob in var_box.submobjects:
                        submob.set_z_index(6)
        for annotation in helper.annotations:
            self.scene.bring_to_front(annotation)
        helper.highlight_lines(11, 12, IBM_GREEN_20)
        self.scene.wait(1.0)
        self.scene.wait(1.0)
        helper.tear_down()


class UnpackingAnimator:
    CODE = """def add(a, b, c):
    return a + b + c

values = [2, 4, 6]
result = add(*values)

def describe_person(name, age, city):
    return f"{name} is {age} and lives in {city}"

info = {"name": "Nam", "age": 18, "city": "Hanoi"}
message = describe_person(**info)"""

    def __init__(self, scene: AnimatedCodeScene):
        self.scene = scene

    def play(self):
        helper = CodeSectionHelper(
            self.scene,
            "Unpacking Iterables Into Arguments",
            self.CODE,
            code_scale=0.6,
            vars_per_row=2
        ).setup()

        helper.highlight_lines(1, 2, IBM_BLUE_20)
        helper.highlight_lines(4, 5, IBM_CYAN_60)

        values_list = List([2, 4, 6])
        values_list.scale(0.7)
        values_list.next_to(helper.variables, DOWN, buff=0.8)
        values_list.align_to(helper.variables.get_left() + [-0.5, 0, 0], LEFT)
        helper.add_annotation(values_list, auto_position=False)

        unpack_text = Text(
            "*values feeds each number into a, b, and c.",
            font_size=24, font=ROBOTO_MONO, color=IBM_CYAN_60
        )
        helper.add_annotation(unpack_text, auto_position=True, buff=1.0, column='variables')

        self.scene.create_variable('values', '[2, 4, 6]')
        self.scene.create_variable('result', 12)

        helper.highlight_lines(7, 8, IBM_BLUE_20)
        helper.highlight_lines(10, 11, IBM_MAGENTA_60)

        info_text = Text(
            "**info pairs dictionary keys to keyword arguments.",
            font_size=24, font=ROBOTO_MONO, color=IBM_MAGENTA_60
        )
        helper.add_annotation(info_text, auto_position=True, anchor=unpack_text, buff=0.3, column='variables')

        self.scene.create_variable('info', '{"name": "Nam", "age": 18, "city": "Hanoi"}')
        self.scene.create_variable('message', 'Nam is 18 and lives in Hanoi')
        self.scene.wait(1.0)

        helper.tear_down()


class FunctionIntroductionScene(AnimatedCodeScene):
    def construct(self):
        # Initialize AnimatedCodeScene state
        super().construct()

        # Set background color
        self.camera.background_color = WHITE

        # Title
        title = Text("Introduction to Python Functions", font_size=48, font=ROBOTO_MONO, color=BLACK)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)

        # Part 1: Motivation
        self.show_motivation(title)

        # Part 2: Mathematical Analogy
        self.show_mathematical_analogy()

        # Part 3: Definition and Benefits
        self.show_definition_and_benefits()

        # Part 4: Function Syntax
        self.show_function_syntax()

        # Part 5: Calling Functions
        self.show_function_calling()

        # Part 6: Return Values
        self.show_return_values()

        # Part 7: Function Examples
        self.show_function_examples()

        # Part 8: Nested Functions
        self.show_nested_functions()

        # Part 9: Docstrings
        self.show_docstrings()

        # Part 10: Unpacking Arguments
        self.show_unpacking_arguments()

        # Part 11: How Functions Work Internally
        self.show_function_execution_details()

        # Part 12: Transition
        self.show_transition()

    def show_motivation(self, title):
        """Part 1: Why we need functions"""
        # Clear title and show motivation
        self.play(FadeOut(title))

        # Question
        question = Text("What if you have a piece of code", font_size=36, font=ROBOTO_MONO, color=BLACK)
        question2 = Text("that you need to use again and again?", font_size=36, font=ROBOTO_MONO, color=BLACK)
        question.next_to(question2, UP, buff=0.2)

        question_group = VGroup(question, question2)
        question_group.move_to(ORIGIN + UP * 1)

        self.play(Write(question_group))
        self.wait(1)

        # Show copy-paste problem
        code_block = """print("Hello, Alice!")
greeting = "Hello, Alice!"
print(greeting)
message = "Hello, Alice!"
print(message)"""

        code_display = CodeWindow(code_block, tab_width=4)
        code_display.scale(0.8).move_to(DOWN * 1.5)

        self.play(FadeIn(code_display))
        self.wait(1)

        # Highlight the repetition
        highlight_rects = []
        for i in [1, 3, 5]:  # Lines with "Hello, Alice!"
            rect = SurroundingRectangle(code_display[f'line_{i}'], color=IBM_RED_60, buff=0.1)
            highlight_rects.append(rect)

        self.play(*[Create(rect) for rect in highlight_rects])
        self.wait(1)

        problem_text = Text("Copy-paste is messy and hard to maintain!", font_size=28, font=ROBOTO_MONO, color=IBM_RED_60)
        problem_text.to_edge(DOWN, buff=0.5)
        self.play(Write(problem_text))
        self.wait(1)

        # Transition to solution
        self.play(
            FadeOut(question_group),
            FadeOut(code_display),
            *[FadeOut(rect) for rect in highlight_rects],
            FadeOut(problem_text)
        )

        # Show function solution
        solution_text = Text("Use a FUNCTION instead!", font_size=42, font=ROBOTO_MONO, color=IBM_GREEN_20)
        solution_text.move_to(ORIGIN)
        self.play(Write(solution_text))
        self.wait(1)

        function_code = """def greet(name):
    return f"Hello, {name}!"

# Now use it anywhere!
print(greet("Alice"))
print(greet("Bob"))
print(greet("Charlie"))"""

        function_display = CodeWindow(function_code, tab_width=4)
        function_display.scale(0.7).move_to(DOWN * 1)

        self.play(FadeOut(solution_text), FadeIn(function_display))
        self.wait(2)

        benefit_text = Text("Write once, use anywhere!", font_size=32, font=ROBOTO_MONO, color=IBM_BLUE_60)
        benefit_text.to_edge(DOWN, buff=0.5)
        self.play(Write(benefit_text))
        self.wait(1)

        self.play(FadeOut(function_display), FadeOut(benefit_text))

    def show_mathematical_analogy(self):
        """Part 2: Mathematical analogy"""
        math_title = Text("Mathematical Analogy", font_size=42, font=ROBOTO_MONO, color=BLACK)
        math_title.to_edge(UP, buff=0.5)
        self.play(Write(math_title))

        # Show mathematical function
        math_eq = Tex(r"$y = a + b$", font_size=48, color=BLACK)
        math_eq.move_to(ORIGIN + UP * 1)

        inputs_text = Text("Inputs: a, b", font_size=28, font=ROBOTO_MONO, color=IBM_BLUE_60)
        inputs_text.next_to(math_eq, DOWN, buff=0.8)

        process_text = Text("Process: addition", font_size=28, font=ROBOTO_MONO, color=IBM_GREEN_20)
        process_text.next_to(inputs_text, DOWN, buff=0.3)

        output_text = Text("Output: y", font_size=28, font=ROBOTO_MONO, color=IBM_RED_60)
        output_text.next_to(process_text, DOWN, buff=0.3)

        self.play(Write(math_eq))
        self.wait(0.5)
        self.play(Write(inputs_text))
        self.wait(0.5)
        self.play(Write(process_text))
        self.wait(0.5)
        self.play(Write(output_text))
        self.wait(1)

        # Show Python function analogy
        python_analogy = Text("Python functions work the same way!", font_size=32, font=ROBOTO_MONO, color=BLACK)
        python_analogy.move_to(DOWN * 2)

        self.play(Write(python_analogy))
        self.wait(1)

        self.play(
            FadeOut(math_title), FadeOut(math_eq), FadeOut(inputs_text),
            FadeOut(process_text), FadeOut(output_text), FadeOut(python_analogy)
        )

    def show_definition_and_benefits(self):
        """Part 3: Definition and benefits table"""
        def_title = Text("What is a Function?", font_size=42, font=ROBOTO_MONO, color=BLACK)
        def_title.to_edge(UP, buff=0.5)
        self.play(Write(def_title))

        definition = Text(
            "A function is a reusable block of code\n"
            "designed to perform a specific task.",
            font_size=32, font=ROBOTO_MONO, color=BLACK
        )
        definition.next_to(def_title, DOWN, buff=0.8)
        definition.move_to([0, definition.get_y(), 0])  # Center horizontally
        definition.move_to([0, definition.get_y(), 0])  # Center horizontally

        self.play(Write(definition))
        self.wait(1)

        # Benefits as a simple list instead of table
        benefits = [
            "• Abstraction: Hides complex details",
            "• Encapsulation: Keeps logic grouped and protected",
            "• Modularity: Breaks programs into smaller parts",
            "• Reusability: Write once, use anywhere",
            "• Maintainability: Easier to update or fix",
            "• Testability: Each function can be tested individually"
        ]

        benefit_texts = []
        for i, benefit in enumerate(benefits):
            text = Text(benefit, font_size=24, font=ROBOTO_MONO, color=BLACK)
            text.move_to(ORIGIN + UP * (2 - i * 0.4))
            benefit_texts.append(text)

        # Fade out definition before showing benefits
        self.play(FadeOut(definition))

        # Fade out previous benefit before showing the next
        for idx, text in enumerate(benefit_texts):
            if idx > 0:
                self.play(FadeOut(benefit_texts[idx-1]))
            self.play(Write(text))
            self.wait(0.3)
        # Fade out the last benefit after all are shown
        self.play(FadeOut(benefit_texts[-1]))

        # Fade out the title at the end of the section
        self.play(FadeOut(def_title))

    def show_function_syntax(self):
        """Part 4: Function syntax"""
        syntax_title = Text("Function Syntax", font_size=42, font=ROBOTO_MONO, color=BLACK)
        syntax_title.to_edge(UP, buff=0.5)
        self.play(Write(syntax_title))

        # General syntax
        syntax_code = """def function_name(parameters):
    # body of the function
    statement(s)
    return value"""

        syntax_display = CodeWindow(syntax_code, tab_width=4)
        syntax_display.scale(0.8).move_to(ORIGIN)

        self.play(FadeIn(syntax_display))
        self.wait(1)

        # Highlight parts
        parts = [
            ("def", "Keyword to define function", IBM_BLUE_60),
            ("function_name", "Name of the function", IBM_GREEN_20),
            ("parameters", "Inputs to the function", IBM_RED_60),
            ("return", "Sends result back", IBM_PURPLE_60)
        ]

        highlights = []
        for part, desc, color in parts:
            if part == "def":
                highlight = syntax_display['line_1'][:3]
            elif part == "function_name":
                highlight = syntax_display['line_1'][4:17]
            elif part == "parameters":
                highlight = syntax_display['line_1'][18:-2]
            elif part == "return":
                highlight = syntax_display['line_3'][:6]

            rect = SurroundingRectangle(highlight, color=color, buff=0.05)
            highlights.append(rect)

        for rect in highlights:
            self.play(Create(rect))
            self.wait(0.5)

        # Example
        example_title = Text("Example:", font_size=32, font=ROBOTO_MONO, color=BLACK)
        example_title.to_edge(DOWN, buff=2)

        example_code = """def add(a, b):
    return a + b"""

        example_display = CodeWindow(example_code, tab_width=4)
        example_display.scale(0.7).next_to(example_title, DOWN, buff=0.3)

        self.play(Write(example_title), FadeIn(example_display))
        self.wait(1)

        self.play(
            FadeOut(syntax_title), FadeOut(syntax_display),
            *[FadeOut(rect) for rect in highlights],
            FadeOut(example_title), FadeOut(example_display)
        )

    def show_function_calling(self):
        """Part 5: Calling functions"""
        call_title = Text("Calling Functions", font_size=42, font=ROBOTO_MONO, color=BLACK)
        call_title.to_edge(UP, buff=0.5)
        self.play(Write(call_title))

        # Positional arguments
        pos_title = Text("Positional Arguments", font_size=32, font=ROBOTO_MONO, color=IBM_BLUE_60)
        pos_title.move_to(ORIGIN + UP * 2)

        pos_code = """result = add(3, 5)"""
        pos_display = CodeWindow(pos_code, tab_width=4)
        pos_display.scale(0.7).next_to(pos_title, DOWN, buff=0.3)

        pos_explain = Text("3 goes to 'a', 5 goes to 'b'", font_size=24, font=ROBOTO_MONO, color=BLACK)
        pos_explain.next_to(pos_display, DOWN, buff=0.3)

        self.play(Write(pos_title), FadeIn(pos_display), Write(pos_explain))
        self.wait(1)

        # Keyword arguments
        kw_title = Text("Keyword Arguments", font_size=32, font=ROBOTO_MONO, color=IBM_GREEN_20)
        kw_title.next_to(pos_explain, DOWN, buff=1)

        kw_code = """result = add(b=10, a=2)"""
        kw_display = CodeWindow(kw_code, tab_width=4)
        kw_display.scale(0.7).next_to(kw_title, DOWN, buff=0.3)

        kw_explain = Text("Explicitly specify which value goes to which parameter", font_size=24, font=ROBOTO_MONO, color=BLACK)
        kw_explain.next_to(kw_display, DOWN, buff=0.3)

        self.play(Write(kw_title), FadeIn(kw_display), Write(kw_explain))
        self.wait(1)

        self.play(
            FadeOut(call_title), FadeOut(pos_title), FadeOut(pos_display), FadeOut(pos_explain),
            FadeOut(kw_title), FadeOut(kw_display), FadeOut(kw_explain)
        )

    def show_return_values(self):
        """Part 6: Return values"""
        return_title = Text("What Functions Can Do", font_size=42, font=ROBOTO_MONO, color=BLACK)
        return_title.to_edge(UP, buff=0.5)
        self.play(Write(return_title))

        # Three types
        types = [
            ("Side Effect", "Modifies environment (e.g., prints output)", IBM_RED_60),
            ("Return Value", "Sends result back to caller", IBM_BLUE_60),
            ("Both", "Does both side effect and returns value", IBM_GREEN_20)
        ]

        type_groups = []
        for i, (name, desc, color) in enumerate(types):
            type_text = Text(name, font_size=32, font=ROBOTO_MONO, color=color)
            desc_text = Text(desc, font_size=24, font=ROBOTO_MONO, color=BLACK)
            desc_text.next_to(type_text, DOWN, buff=0.2)

            group = VGroup(type_text, desc_text)
            group.move_to(ORIGIN + UP * (1.5 - i * 1.5))
            type_groups.append(group)

        for group in type_groups:
            self.play(Write(group))
            self.wait(0.8)

        self.wait(1)

        self.play(FadeOut(return_title), *[FadeOut(group) for group in type_groups])

    def show_function_examples(self):
        """Part 7: Function examples"""
        examples_title = Text("Function Examples", font_size=42, font=ROBOTO_MONO, color=BLACK)
        examples_title.to_edge(UP, buff=0.5)
        self.play(Write(examples_title))

        # Example 1: Side effect
        ex1_title = Text("1. Side Effect Only", font_size=32, font=ROBOTO_MONO, color=IBM_RED_60)
        ex1_title.move_to(ORIGIN + UP * 2)

        ex1_code = """def say_hello(name):
    print(f"Hello, {name}!")"""
        ex1_display = CodeWindow(ex1_code, tab_width=4)
        ex1_display.scale(0.6).next_to(ex1_title, DOWN, buff=0.3)

        ex1_desc = Text("Prints to console, returns nothing", font_size=22, font=ROBOTO_MONO, color=BLACK)
        ex1_desc.next_to(ex1_display, DOWN, buff=0.2)

        self.play(Write(ex1_title), FadeIn(ex1_display), Write(ex1_desc))
        self.wait(1)

        # Example 2: Return value
        ex2_title = Text("2. Return Value Only", font_size=32, font=ROBOTO_MONO, color=IBM_BLUE_60)
        ex2_title.next_to(ex1_desc, DOWN, buff=0.8)

        ex2_code = """def square(x):
    return x ** 2"""
        ex2_display = CodeWindow(ex2_code, tab_width=4)
        ex2_display.scale(0.6).next_to(ex2_title, DOWN, buff=0.3)

        ex2_desc = Text("Returns squared value to caller", font_size=22, font=ROBOTO_MONO, color=BLACK)
        ex2_desc.next_to(ex2_display, DOWN, buff=0.2)

        self.play(Write(ex2_title), FadeIn(ex2_display), Write(ex2_desc))
        self.wait(1)

        # Example 3: Both
        ex3_title = Text("3. Both Side Effect and Return", font_size=32, font=ROBOTO_MONO, color=IBM_GREEN_20)
        ex3_title.next_to(ex2_desc, DOWN, buff=0.8)

        ex3_code = """def greet_and_return(name):
    print("Greeting sent!")
    return f"Hello, {name}" """
        ex3_display = CodeWindow(ex3_code, tab_width=4)
        ex3_display.scale(0.6).next_to(ex3_title, DOWN, buff=0.3)

        ex3_desc = Text("Prints message AND returns greeting", font_size=22, font=ROBOTO_MONO, color=BLACK)
        ex3_desc.next_to(ex3_display, DOWN, buff=0.2)

        self.play(Write(ex3_title), FadeIn(ex3_display), Write(ex3_desc))
        self.wait(1)

        self.play(
            FadeOut(examples_title), FadeOut(ex1_title), FadeOut(ex1_display), FadeOut(ex1_desc),
            FadeOut(ex2_title), FadeOut(ex2_display), FadeOut(ex2_desc),
            FadeOut(ex3_title), FadeOut(ex3_display), FadeOut(ex3_desc)
        )

    def show_nested_functions(self):
        """Part 8: Nested functions"""
        NestedFunctionAnimator(self).play()

    def show_docstrings(self):
        """Part 9: Function docstrings"""
        DocstringAnimator(self).play()

    def show_unpacking_arguments(self):
        """Part 10: Unpacking arguments"""
        UnpackingAnimator(self).play()

    def show_function_execution_details(self):
        """Part 11: Detailed function execution animation"""
        # Clear previous content
        self.next_section(name="How Functions Work Internally")

        # Setup code and variables for detailed animation
        execution_title = Text("How Functions Work Internally", font_size=42, font=ROBOTO_MONO, color=BLACK)
        execution_title.to_edge(UP, buff=0.5)
        self.play(Write(execution_title))

        # Function code for demonstration
        function_code = """def calculate_total(price, tax_rate):
    tax_amount = price * tax_rate
    total = price + tax_amount
    return total

# Call the function
result = calculate_total(100, 0.08)
print(f"Total: ${result}")"""

        code = CodeWindow(function_code, tab_width=4)
        code.scale(0.7).align_to([-6.5, 2.0, 0], UL)
        code.set_opacity(0)
        self.set_code(code)
        self.play(FadeIn(code))

        variables = VariableArea()
        variables.align_to([4.5, 2.0, 0], UR)
        variables.set_opacity(0)
        self.set_variables(variables)
        self.play(FadeIn(variables))

        step_label = Text("Step 1: Define the function", font_size=28, font=ROBOTO_MONO, color=BLACK)
        step_label.to_edge(DOWN, buff=0.7)
        self.play(Write(step_label))

        def update_step(text: str):
            new_label = Text(text, font_size=28, font=ROBOTO_MONO, color=BLACK)
            new_label.to_edge(DOWN, buff=0.7)
            self.play(Transform(step_label, new_label))

        def flash_line(line_no: int, color=IBM_CYAN_60, hold: float = 0.6):
            line_group = code[f'line_{line_no}']
            highlight = SurroundingRectangle(line_group, color=color, buff=0.08)
            highlight.set_fill(color, 0.12)
            highlight.set_stroke(color, width=2)
            self.play(Create(highlight))
            self.wait(hold)
            self.play(FadeOut(highlight))

        # Step 1: Highlight function definition
        self.play(self.move_pc(1, 0, 3))
        self.play(self.highlight_scope('def', lines=4))
        flash_line(1, IBM_BLUE_20)
        self.pause()

        # Create function visualization
        calc_fn = Function('calculate_total()', 'Calculate total\nwith tax',
                          num_inputs=2, num_outputs=1, user_fn=True)
        self.set_functions_anchor((code.get_corner(UR) + variables.get_corner(UL)) / 2)
        self.animate_user_fn(calc_fn, code_group=code.lines(1, 4),
                           name_group=code['line_1'][4:19],
                           inputs_group=code['line_1'][20:-2],
                           outputs_groups=[code['line_4']])
        self.pause()

        # Step 2: Function call
        update_step("Step 2: Call the function")
        self.play(self.move_pc(6, 0, None))
        flash_line(6)
        self.pause()

        # Animate parameter passing
        price_input = code_value('100').scale(1.2).next_to(calc_fn['input_1'], LEFT, buff=0.1)
        tax_input = code_value('0.08').scale(1.2).next_to(calc_fn['input_2'], LEFT, buff=0.1)

        self.play(*self.cross_fade(code['line_6'][22:25].copy(), price_input, layer=2))
        self.play(*self.cross_fade(code['line_6'][27:-1].copy(), tax_input, layer=2))

        # Create PC for function execution
        calc_pc = create_pc(VGroup(price_input, tax_input, calc_fn))
        self.play(Create(calc_pc))

        # Push function stack
        push_anim = variables.push_variable_stack(initial_lines=2, vars_per_row=2)
        pc_anim = self.push_pc(1, 14, -2, init_pc=calc_pc)
        self.play(push_anim)
        self.play(pc_anim)
        self.pause()

        update_step("Step 3: Bind parameters in a new frame")

        # Move inputs into function parameters
        self.play(
            price_input.animate.next_to(calc_fn['input_1'], RIGHT, buff=0.1),
            tax_input.animate.next_to(calc_fn['input_2'], RIGHT, buff=0.1)
        )
        self.create_variable('price', 100, source=price_input)
        self.create_variable('tax_rate', 0.08, source=tax_input)
        self.pause()

        # Step 4: Execute function body
        update_step("Step 4: Execute the function body")
        self.play(self.move_pc(2, 0, None))
        flash_line(2)
        tax_calc, tax_value = self.numeric_calculation('price', 'tax_rate', '*')
        # Create the tax_amount variable so it can be referenced later
        tax_var = self.create_variable('tax_amount', tax_value, source=tax_calc)
        self.pause()

        self.play(self.move_pc(3, 0, None))
        flash_line(3)
        total_calc, total_value = self.numeric_calculation('price', 'tax_amount', '+')
        self.pause()

        # Step 5: Return value
        update_step("Step 5: Return the value to the caller")
        self.play(self.move_pc(4, 0, None))
        flash_line(4, IBM_GREEN_20)
        return_value = total_calc.copy()
        return_target = return_value.copy().next_to(calc_fn['output_1'], RIGHT, buff=0.1)
        self.play(return_value.animate.become(return_target))
        self.pause()

        # Pop function and return to caller
        variables.pop_variable_stack(self)
        self.pop_pc()
        self.wait(0.5)

        # Step 6: Assign result
        update_step("Step 6: Store and use the result")
        self.play(self.move_pc(6, 0, 6))
        flash_line(6, IBM_BLUE_20, hold=0.4)
        result_var = self.create_variable('result', 108.0, source=return_value)
        self.pause()

        # Step 6: Print result
        self.play(self.move_pc(7, 0, None))
        flash_line(7, IBM_GREEN_20, hold=0.4)
        print_text = Text('Total: $108.0', font_size=24, font=LM_MONO, color=IBM_GREEN_20)
        print_text.to_edge(DOWN, buff=1)
        self.play(FadeIn(print_text))
        self.wait(2)

        # Clean up
        self.play(
            FadeOut(execution_title), FadeOut(code), FadeOut(variables),
            FadeOut(calc_fn), FadeOut(print_text), FadeOut(result_var['box']), FadeOut(result_var['contents']),
            FadeOut(step_label)
        )

    def show_transition(self):
        """Part 8: Transition to next section"""
        transition_text = Text(
            "Now that we understand functions,\n"
            "let's apply this knowledge in a fun way!",
            font_size=36, font=ROBOTO_MONO, color=BLACK
        )
        transition_text.move_to(ORIGIN)

        self.play(Write(transition_text))
        self.wait(1)

        next_section = Text(
            "Next: Dice Game – Predicting Tài or Xỉu\n"
            "with random.seed()",
            font_size=32, font=ROBOTO_MONO, color=IBM_BLUE_60
        )
        next_section.next_to(transition_text, DOWN, buff=0.8)

        self.play(Write(next_section))
        self.wait(2)

        # Fade out everything
        self.play(FadeOut(transition_text), FadeOut(next_section))


# Render this with:
# manim render -ql function_introduction.py FunctionIntroductionScene
