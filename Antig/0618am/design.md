svm_kernel_trick_project:
  title: "SVM Kernel Trick 3D Interactive Demo"
  version: "v2"
  role: "You are a professional machine learning developer, designer, and educational content creator."
  
  objective: >
    Implement a complete educational suite for demonstrating and exploring the Support Vector Machine (SVM) kernel trick in 3D.
    The suite includes a concept animation (Manim and Matplotlib versions), a static mathematical decision surface plot using Matplotlib,
    and a light-themed interactive dashboard using Streamlit and Plotly.

  environment:
    python: "3.13 or 3.14 on Windows"
    dependencies:
      - "manim"
      - "numpy"
      - "scikit-learn"
      - "matplotlib"
      - "streamlit"
      - "plotly"
      - "pandas"

  shared_utilities:
    data_generator:
      file: "utils/data_generator.py"
      functions:
        - name: "generate_ring_dataset"
          parameters:
            n_inner: "Number of points in the inner ring (default 35)"
            n_outer: "Number of points in the outer ring (default 45)"
            inner_radius_range: "Tuple for inner ring boundary (default 0.0 to 1.0)"
            outer_radius_range: "Tuple for outer ring boundary (default 1.6 to 2.5)"
            noise: "Gaussian noise standard deviation (default 0.08)"
            random_seed: "Seed for reproducibility (default 7)"
          returns: "X (coordinates), y (class labels 0 or 1)"

    svm_utils:
      file: "utils/svm_utils.py"
      functions:
        - name: "train_svm"
          description: "Trains an sklearn SVC model using specified kernel, C, gamma, and degree parameters."
        - name: "make_decision_grid"
          description: "Generates a 2D meshgrid based on the bounding box of input features X."
        - name: "compute_decision_surface"
          description: "Computes decision function scores f(x, y) on meshgrid points and reshapes to grid format."

  phases:
    phase_1_manim_animation:
      file: "phase1_manim_kernel_trick.py"
      class_name: "SVMKernelTrick3D"
      parent_class: "ThreeDScene"
      description: >
        Renders a conceptual 3D animation demonstrating why non-linearly separable points in 2D become linearly separable in 3D.
      steps:
        1_title_screen:
          - "Display a sleek title: 'SVM Kernel Trick: From 2D to 3D'"
          - "Fade out after a short pause."
        2_flat_2d_view:
          - "Align camera to a top-down, flat 2D perspective (phi=0, theta=-90 degrees)."
          - "Scatter points on z=0 plane: Class 0 (BLUE) inside, Class 1 (RED) outside."
        3_3d_perspective:
          - "Animate camera to a 3D isometric angle (phi=65, theta=-45 degrees)."
          - "Display the feature mapping formula: phi(x, y) = (x, y, x^2 + y^2)."
        4_feature_lifting:
          - "Lift dots along Z-axis based on their feature coordinates: z = x^2 + y^2."
          - "Plot translucent paraboloid mapping surface."
        5_separating_hyperplane:
          - "Introduce a translucent yellow separating hyperplane at z = 2.0."
        6_decision_boundary_projection:
          - "Draw intersection circle (radius = sqrt(2.0)) and project it back to the 2D plane."
        7_camera_rotation:
          - "Rotate camera continuously to showcase linear separation from multiple angles."

    phase_1_alt_matplotlib_animation:
      file: "phase1_matplotlib_animation.py"
      description: >
        Lightweight alternative using Matplotlib's FuncAnimation and PillowWriter to render the exact same 3D lifting
        and hyperplane separation story into an interactive window or a GIF file without requiring external Manim or FFmpeg.

    phase_2_decision_surface:
      file: "phase2_rbf_decision_surface.py"
      description: >
        Trains a real Support Vector Classifier with RBF kernel and visualizes the decision contours in 2D and decision surface in 3D.
      steps:
        1_train_model:
          - "Train a scikit-learn SVC model with RBF kernel (C=10.0, gamma=1.0) on ring data."
        2_plot_2d_subplot:
          - "Plot contourf of decision scores, margins (f(x, y) = -1, 1), and boundary (f(x, y) = 0)."
          - "Scatter data points and highlight support vectors with yellow circles."
        3_plot_3d_subplot:
          - "Plot 3D surface z = f(x, y), reference plane z = 0, and data points lifted to their decision scores."
        4_save_plot:
          - "Save the side-by-side figure to 'outputs/rbf_decision_surface.png'."

    phase_3_interactive_streamlit:
      file: "phase3_streamlit_app.py"
      description: >
        Implements a light-themed interactive 3D studio that guides users through the concept mapping and trained SVM decision surfaces.
      ui_aesthetics:
        typography: "Outfit (English) and Noto Sans TC (Traditional Chinese) fonts"
        theme: "Clean, modern light-themed studio"
        background_color: "#f8fafc (Light slate)"
        layout: "Three-column grid configuration: columns([1.1, 2.5, 1.1])"
        cards: "White background cards with thin borders (#e2e8f0) and subtle drop shadows"
      components:
        header_bar:
          - "Display WebGL 3D badge and logo on a clean white navigation bar at the top"
        left_column_control_panel:
          - "Section 1 (Dataset Config): Sliders for sample size and noise; button to regenerate data"
          - "Section 2 (Workflow Steps): Interactive clickable buttons for STEP 1 (2D space) and STEP 2 (3D mapping)"
          - "Section 3 (Detail Controls): Toggles for Hyperplane, Support Vectors, Margins, and RBF Kernel (disabled in STEP 1)"
          - "Section 4 (RBF Hyperparameters): Sliders for C and Gamma (visible only if RBF is toggled ON)"
        center_column_visualization:
          - "Light-themed 3D Plotly chart representing points and surfaces"
          - "In STEP 1: All points and grid coordinates lie on z = 0 plane"
          - "In STEP 2 (Explicit Paraboloid): Z coordinates map to x^2 + y^2; hyperplane is at z = 2.0; margins are at z = 1.0 and 3.0"
          - "In STEP 2 (Implicit RBF): Z coordinates map to trained SVM decision scores; hyperplane is at z = 0.0; margins are at z = ±1.0"
          - "Display a metrics box (Model type, Accuracy, Support Vectors count) above the chart when RBF is ON"
        right_column_academic_explanation:
          - "Dynamic text explanation explaining the selected STEP's mathematical meaning in Traditional Chinese"
          - "Emerald-colored highlight callout boxes summarizing key takeaways"
          - "A mini log box at the bottom showing Antigravity agent dialogue status"

  run_commands:
    phase_1: "python -m manim -pql phase1_manim_kernel_trick.py SVMKernelTrick3D"
    phase_1_alt: "python phase1_matplotlib_animation.py"
    phase_2: "python phase2_rbf_decision_surface.py"
    phase_3: "streamlit run phase3_streamlit_app.py"

  constraints:
    - "All code must be fully translated to Traditional Chinese for the UI labels, explanations, and observations."
    - "Ensure all Plotly figures use a white/light paper background and light gray gridlines to fit the light theme."
    - "Ensure Streamlit UI elements safely use st.markdown to inject customized styling without breaking core inputs."
