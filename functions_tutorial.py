from manim import *

from manim_ace.code import CodeWindow
from manim_ace.colors import (IBM_BLUE_60, IBM_RED_60, BLACK_19, TRUE_BACKGROUND_COLOR, FALSE_BACKGROUND_COLOR,
                              IBM_CYAN_60, IBM_MAGENTA_60, IBM_PURPLE_60,
                              SECONDARY_RECT_COLOR, IBM_GREEN_20,
                              IBM_BLUE_20, TOL_ORANGE)
from manim_ace.fonts import LM_MONO, ROBOTO_MONO
from manim_ace.functions import Function
from manim_ace.scene import AnimatedCodeScene, create_pc
from manim_ace.utils import become_in_place, surround, occlude
from manim_ace.variables import VariableArea, code_value


# Code examples for the tutorial
greeting_function_code = """
def greet(name):
    message = "Hello, " + name + "!"
    return message

# Call the function
result = greet("Alice")
print(result)
"""

area_function_code = """
def calculate_area(length, width):
    area = length * width
    return area

# Real-world example: Calculate room area
room_length = 5.5
room_width = 4.2
room_area = calculate_area(room_length, room_width)
print(f"Room area: {room_area} square meters")
"""

class FunctionsTutorialScene(AnimatedCodeScene):
    def construct(self):
        super().construct()

        # Title
        title = Text("Functions in Python", font_size=48, font=ROBOTO_MONO, color=BLACK)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)

        # Introduction text
        intro_text = Text(
            "Functions are reusable blocks of code that perform specific tasks.\n"
            "They help organize code and avoid repetition.",
            font_size=24, font=ROBOTO_MONO, color=BLACK
        )
        intro_text.next_to(title, DOWN, buff=0.8)
        intro_text.move_to([0, intro_text.get_y(), 0])  # Center horizontally
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # Set up code window and variables
        code = CodeWindow(greeting_function_code, tab_width=4)
        code.scale(0.7).align_to([-7.0, 2.5, 0], UL)
        self.set_code(code)
        self.pause()

        variables = VariableArea()
        variables.align_to([5.5, 2.5, 0], UR)
        self.set_variables(variables)
        self.play(FadeIn(variables))
        self.pause()

        # Highlight function definition
        self.play(self.move_pc(1, 0, 3))
        self.play(self.highlight_scope('def', lines=3))
        self.pause()

        # Create function visualization
        greet_fn = Function('greet()', 'Create greeting\nmessage',
                           num_inputs=1, num_outputs=1, user_fn=True)
        self.set_functions_anchor((code.get_corner(UR) + variables.get_corner(UL)) / 2)
        self.animate_user_fn(greet_fn, code_group=code.lines(1, 3),
                           name_group=code['line_1'][4:9],
                           inputs_group=code['line_1'][10:-2],
                           outputs_groups=[code['line_3']])
        self.pause()

        # Show function call
        self.play(self.move_pc(6, 0, None))
        self.pause()

        # Animate function call
        input_name = code_value('"Alice"').scale(1.2).next_to(greet_fn['input_1'], LEFT, buff=0.1)
        self.play(*self.cross_fade(code['line_6'][13:-2].copy(), input_name, layer=2))

        # Create PC for function execution
        greet_pc = create_pc(VGroup(input_name, greet_fn))
        self.play(Create(greet_pc))

        push_anim = variables.push_variable_stack(initial_lines=2, vars_per_row=2)
        pc_anim = self.push_pc(1, 14, -2, init_pc=greet_pc)
        self.play(push_anim)
        self.play(pc_anim)
        self.pause()

        # Move input into function
        self.play(input_name.animate.next_to(greet_fn['input_1'], RIGHT, buff=0.1))
        self.create_variable('name', '"Alice"', source=input_name)
        self.pause()

        # Execute function body
        self.play(self.move_pc(2, 0, None))
        message_var = self.create_variable('message', '"Hello, Alice!"', show_value=False)
        self.pause()

        # Return value
        self.play(self.move_pc(3, 0, None))
        return_value = message_var['contents'].copy()
        return_target = return_value.copy().next_to(greet_fn['output_1'], RIGHT, buff=0.1)
        self.play(return_value.animate.become(return_target))
        self.pause()

        # Pop function and assign result
        variables.pop_variable_stack(self)
        self.pop_pc()
        self.wait(0.5)

        # Assign result to variable
        self.play(self.move_pc(6, 0, 6))
        result_var = self.create_variable('result', '"Hello, Alice!"', source=return_value)
        self.pause()

        # Print result
        self.play(self.move_pc(7, 0, None))
        print_text = Text('Hello, Alice!', font_size=24, font=LM_MONO, color=IBM_BLUE_60)
        print_text.to_edge(DOWN, buff=1)
        self.play(FadeIn(print_text))
        self.wait(2)

        # Transition to real-world example
        self.play(FadeOut(print_text), FadeOut(result_var['box']), FadeOut(result_var['contents']))
        transition_text = Text("Now let's see a real-world example:", font_size=32, font=ROBOTO_MONO, color=BLACK)
        transition_text.move_to([0, 1, 0])
        self.play(Write(transition_text))
        self.wait(1)

        # Switch to area calculation code
        new_code = CodeWindow(area_function_code, tab_width=4)
        new_code.scale(0.7).align_to([-7.0, 2.5, 0], UL)
        self.play(FadeOut(code), FadeIn(new_code), FadeOut(transition_text))
        self.set_code(new_code)
        self.pause()

        # Clear old function
        self.functions.remove(greet_fn)

        # Highlight area function definition
        self.play(self.move_pc(1, 0, 3))
        self.play(self.highlight_scope('def', lines=3))
        self.pause()

        # Create area function visualization
        area_fn = Function('calculate_area()', 'Calculate\nrectangle area',
                          num_inputs=2, num_outputs=1, user_fn=True)
        self.animate_user_fn(area_fn, code_group=new_code.lines(1, 3),
                           name_group=new_code['line_1'][4:19],
                           inputs_group=new_code['line_1'][20:-2],
                           outputs_groups=[new_code['line_3']])
        self.pause()

        # Show variable assignments
        self.play(self.move_pc(6, 0, None))
        length_var = self.create_variable('room_length', 5.5, source=new_code['line_6'][0:12])
        self.pause()

        self.play(self.move_pc(7, 0, None))
        width_var = self.create_variable('room_width', 4.2, source=new_code['line_7'][0:11])
        self.pause()

        # Function call
        self.play(self.move_pc(8, 0, None))
        input_length = length_var['contents'].copy()
        input_width = width_var['contents'].copy()

        self.play(
            *self.cross_fade(new_code['line_8'][17:23].copy(), input_length.next_to(area_fn['input_1'], LEFT, buff=0.1), layer=2),
            *self.cross_fade(new_code['line_8'][25:-1].copy(), input_width.next_to(area_fn['input_2'], LEFT, buff=0.1), layer=2)
        )

        # Execute function
        area_pc = create_pc(VGroup(input_length, input_width, area_fn))
        self.play(Create(area_pc))

        push_anim = variables.push_variable_stack(initial_lines=3, vars_per_row=2)
        pc_anim = self.push_pc(1, 14, -2, init_pc=area_pc)
        self.play(push_anim)
        self.play(pc_anim)
        self.pause()

        # Move inputs into function
        self.play(
            input_length.animate.next_to(area_fn['input_1'], RIGHT, buff=0.1),
            input_width.animate.next_to(area_fn['input_2'], RIGHT, buff=0.1)
        )
        self.create_variable('length', 5.5, source=input_length)
        self.create_variable('width', 4.2, source=input_width)
        self.pause()

        # Calculate area
        self.play(self.move_pc(2, 0, None))
        area_calc, area_value = self.numeric_calculation('length', 'width', '*')
        self.pause()

        # Return area
        self.play(self.move_pc(3, 0, None))
        return_area = area_calc.copy()
        return_target = return_area.copy().next_to(area_fn['output_1'], RIGHT, buff=0.1)
        self.play(return_area.animate.become(return_target))
        self.pause()

        # Pop function
        variables.pop_variable_stack(self)
        self.pop_pc()
        self.wait(0.5)

        # Assign result
        self.play(self.move_pc(8, 0, 8))
        room_area_var = self.create_variable('room_area', 23.1, source=return_area)
        self.pause()

        # Print result
        self.play(self.move_pc(9, 0, None))
        result_text = Text('Room area: 23.1 square meters', font_size=24, font=LM_MONO, color=IBM_GREEN_20)
        result_text.to_edge(DOWN, buff=1)
        self.play(FadeIn(result_text))
        self.wait(2)

        # Conclusion
        conclusion = Text(
            "Functions make code modular and reusable!\n"
            "They take inputs, process them, and return outputs.",
            font_size=28, font=ROBOTO_MONO, color=BLACK
        )
        conclusion.move_to([0, -2, 0])  # Center the conclusion text
        self.play(FadeIn(conclusion))
        self.wait(3)


# Render this with:
# manim render -qm functions_tutorial.py FunctionsTutorialScene