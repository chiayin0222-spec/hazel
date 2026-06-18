from manim import *
import numpy as np
from utils.data_generator import generate_ring_dataset

class SVMKernelTrick3D(ThreeDScene):
    def construct(self):
        # 1. Opening Title
        title = Text("SVM Kernel Trick: From 2D to 3D", font_size=40, color=WHITE)
        subtitle = Text("Nonlinear in 2D, linear in 3D feature space", font_size=20, color=GRAY)
        title_group = VGroup(title, subtitle).arrange(DOWN, buffer=0.3)
        
        self.add_fixed_in_frame_mobjects(title_group)
        self.play(Write(title_group))
        self.wait(2)
        self.play(FadeOut(title_group))
        
        # 2. Setup 3D Axes
        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[0, 8, 2],
            x_length=6,
            y_length=6,
            z_length=4,
        )
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES) # 2D flat top-down view
        
        # 3. Generate and Add Data Points on z=0 Plane
        # Use no noise for conceptual animation (clean concentric rings)
        X, y = generate_ring_dataset(
            n_inner=35, 
            n_outer=45, 
            inner_radius_range=(0.2, 1.0), 
            outer_radius_range=(1.8, 2.5), 
            noise=0.03, 
            random_seed=7
        )
        
        dots = VGroup()
        for x_val, y_val, label in zip(X[:, 0], X[:, 1], y):
            color = BLUE if label == 0 else RED
            # Map axes coordinates to scene coordinates
            scene_pos = axes.c2p(x_val, y_val, 0)
            dot = Dot3D(point=scene_pos, color=color, radius=0.06)
            dots.add(dot)
            
        self.play(Create(axes), Create(dots))
        
        # Explanation text in 2D
        exp_text_2d = Text("Original 2D Space: Not linearly separable", font_size=24, color=WHITE)
        exp_text_2d.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(exp_text_2d)
        self.play(Write(exp_text_2d))
        self.wait(2.5)
        self.play(FadeOut(exp_text_2d))
        
        # 4. Move camera to 3D perspective
        self.play(
            self.camera.animate.set_euler_angles(phi=65 * DEGREES, theta=-45 * DEGREES),
            run_time=2.5
        )
        self.wait(1)
        
        # 5. Show mapping formula
        formula = MathTex(r"\phi(x, y) = (x, y, x^2 + y^2)", font_size=36, color=YELLOW)
        formula.to_edge(UP)
        self.add_fixed_in_frame_mobjects(formula)
        
        exp_text_3d = Text("Mapping points to 3D: z = x^2 + y^2", font_size=20, color=WHITE)
        exp_text_3d.next_to(formula, DOWN, buffer=0.2)
        self.add_fixed_in_frame_mobjects(exp_text_3d)
        
        self.play(Write(formula), Write(exp_text_3d))
        self.wait(2)
        
        # 6. Lift points to 3D
        lift_animations = []
        for dot, x_val, y_val in zip(dots, X[:, 0], X[:, 1]):
            z_val = x_val**2 + y_val**2
            target_scene_pos = axes.c2p(x_val, y_val, z_val)
            lift_animations.append(dot.animate.move_to(target_scene_pos))
            
        self.play(*lift_animations, run_time=3)
        self.wait(1.5)
        
        # 7. Draw Paraboloid Surface
        # Formula: z = x^2 + y^2
        # Note: We scale surface coordinates to match the axes.c2p mapping.
        paraboloid = Surface(
            lambda u, v: axes.c2p(u, v, u**2 + v**2),
            u_range=[-2.8, 2.8],
            v_range=[-2.8, 2.8],
            resolution=(25, 25),
            fill_color=BLUE_E,
            fill_opacity=0.22,
            checkerboard_colors=None
        )
        
        self.play(Create(paraboloid), run_time=2)
        self.wait(1)
        
        # 8. Show separating hyperplane
        # Inner ring radius is <= 1.0 (z_max <= 1.0)
        # Outer ring radius is >= 1.8 (z_min >= 3.24)
        # Choose separating hyperplane at z = 2.0
        z_hyper = 2.0
        hyperplane = Surface(
            lambda u, v: axes.c2p(u, v, z_hyper),
            u_range=[-2.8, 2.8],
            v_range=[-2.8, 2.8],
            resolution=(10, 10),
            fill_color=YELLOW_E,
            fill_opacity=0.35,
            checkerboard_colors=None
        )
        
        hyper_label = Text("Hyperplane in Feature Space (z = 2.0)", font_size=20, color=YELLOW)
        hyper_label.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(hyper_label)
        
        self.play(Create(hyperplane), Write(hyper_label), run_time=2)
        self.wait(2)
        
        # 9. Project back to 2D (Decision Circle)
        # The intersection of paraboloid (z = x^2 + y^2) and hyperplane (z = 2.0)
        # is a circle of radius sqrt(2.0) at z = 2.0, projected to z = 0
        r_decision = np.sqrt(z_hyper)
        
        # Generate points of the decision boundary circle in 3D scene space
        t_vals = np.linspace(0, 2 * np.pi, 100)
        decision_boundary_points = [
            axes.c2p(r_decision * np.cos(t), r_decision * np.sin(t), 0)
            for t in t_vals
        ]
        
        decision_boundary = VMobject(color=YELLOW)
        decision_boundary.set_points_as_corners(decision_boundary_points)
        
        self.play(FadeOut(exp_text_3d))
        exp_text_project = Text("Projecting decision boundary back to 2D", font_size=20, color=WHITE)
        exp_text_project.next_to(formula, DOWN, buffer=0.2)
        self.add_fixed_in_frame_mobjects(exp_text_project)
        
        self.play(Write(exp_text_project))
        self.play(Create(decision_boundary), run_time=2)
        self.wait(1.5)
        
        # 10. Rotate Camera to show separation clearly
        self.play(FadeOut(hyper_label), FadeOut(exp_text_project))
        
        # Add summary texts
        summary_title = Text("Key Takeaway:", font_size=24, color=WHITE).to_edge(LEFT).shift(UP * 1.5)
        summary_text1 = Text("• 3D Feature Space: Linear Hyperplane", font_size=18, color=YELLOW).next_to(summary_title, DOWN, alignto=LEFT, buffer=0.3)
        summary_text2 = Text("• Original 2D Space: Circular Boundary", font_size=18, color=YELLOW).next_to(summary_text1, DOWN, alignto=LEFT, buffer=0.2)
        
        self.add_fixed_in_frame_mobjects(summary_title, summary_text1, summary_text2)
        self.play(Write(summary_title), Write(summary_text1), Write(summary_text2))
        
        self.begin_ambient_camera_rotation(rate=0.18)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        # Fade out everything
        self.play(
            FadeOut(axes),
            FadeOut(dots),
            FadeOut(paraboloid),
            FadeOut(hyperplane),
            FadeOut(decision_boundary),
            FadeOut(formula),
            FadeOut(summary_title),
            FadeOut(summary_text1),
            FadeOut(summary_text2)
        )
        self.wait(1)
