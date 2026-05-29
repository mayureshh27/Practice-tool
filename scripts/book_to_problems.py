# /// script
# dependencies = [
#   "pypdf",
#   "google-genai",
#   "python-dotenv",
#   "pydantic",
# ]
# ///

import os
import sys
import json
import argparse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Reconfigure stdout for UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =====================================================================
# Pydantic Schemas for Structured LLM Outputs
# =====================================================================

class Example(BaseModel):
    input: str = Field(description="Sample input representation, e.g. 'R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]'")
    output: str = Field(description="Expected sample output representation, e.g. 'true'")

class Problem(BaseModel):
    id: str = Field(description="Unique string identifier, e.g. 'exercise-2-1'")
    number: int = Field(description="Sequential exercise number")
    title: str = Field(description="Exercise title, e.g. 'Exercise 2.1: Matrix Rotation Verification'")
    chapter: str = Field(description="Chapter ID, e.g. 'ch2'")
    difficulty: str = Field(description="Difficulty level: 'Judgeable' or 'Project'")
    tags: List[str] = Field(description="List of relevant tags, e.g. ['matrix', 'rotation', 'math']")
    statement: str = Field(description="One-sentence description of the task")
    problemText: str = Field(description="Detailed markdown description of the problem and mathematical formulas")
    explanation: str = Field(description="Detailed markdown explanation of the concepts, intuition, and mental model")
    howItWorks: str = Field(description="Detailed markdown of how the solution should be approached")
    syntax: str = Field(description="Syntax references, imports, and Go patterns to reach for")
    solve: str = Field(description="Step-by-step path to solve the exercise")
    lessonTitle: str = Field(default="Intuitive Explanation")
    lesson: str = Field(description="Same as explanation")
    approach: str = Field(description="Same as solve")
    pitfalls: List[str] = Field(description="List of common pitfalls to watch out for")
    hints: List[str] = Field(description="List of progressive hints for the student")
    starterCode: str = Field(description="Valid Go starter code containing the function signature and package main")
    solutionCode: str = Field(description="Valid Go complete solution code")
    testCode: str = Field(description="Valid Go test suite with func main() and assertEqual or delta checks")
    exerciseMode: str = Field(description="Mode of exercise: 'judge' or 'project'")
    verifier: str = Field(description="Verifier type: 'local-tests' (for judge) or 'manual' (for project)")
    examples: List[Example] = Field(description="Input/output examples for UI display")

class Chapter(BaseModel):
    id: str = Field(description="Unique chapter identifier, e.g., 'ch2'")
    title: str = Field(description="Chapter title, e.g., 'Rigid-Body Motions'")
    description: str = Field(description="Short description of concepts covered in this chapter")

class ChaptersList(BaseModel):
    chapters: List[Chapter]

class ProblemsList(BaseModel):
    problems: List[Problem]

# =====================================================================
# High-Quality Mock Database for Modern Robotics (Fallback / Dry Run)
# =====================================================================

MOCK_METADATA = {
    "title": "Modern Robotics",
    "subtitle": "Mechanics, Planning, and Control in Go",
    "language": "go"
}

MOCK_CHAPTERS = [
    {
        "id": "ch2",
        "title": "Rigid-Body Motions",
        "description": "SO(3) rotations, exponential coordinates, skew-symmetric mappings, and rigid-body transforms."
    },
    {
        "id": "ch4",
        "title": "Forward Kinematics",
        "description": "Product of Exponentials (PoE) formula, space and body formulations, and planar robot kinematics."
    },
    {
        "id": "ch9",
        "title": "Trajectory Generation",
        "description": "Point-to-point path planning, cubic and quintic polynomial time scaling, and profile evaluation."
    }
]

MOCK_PROBLEMS = [
    {
        "id": "exercise-2-1",
        "number": 1,
        "title": "Exercise 2.1: Rotation Matrix Verification",
        "chapter": "ch2",
        "difficulty": "Judgeable",
        "tags": ["matrix", "rotation", "math"],
        "statement": "Verify if a 3x3 matrix is a valid SO(3) rotation matrix by checking orthogonality and determinant.",
        "problemText": "Write a function `Solve(R [3][3]float64) bool` that returns `true` if $R$ is a valid member of the Special Orthogonal Group $SO(3)$, and `false` otherwise.\n\n### SO(3) Conditions:\n1. Orthogonality: $R^T R = I$ (the identity matrix).\n2. Handedness: $\\det(R) = 1$.\n\nUse a floating-point tolerance of `1e-5` for comparisons to account for floating-point precision issues.",
        "lessonTitle": "Intuitive Explanation",
        "lesson": "### What you are learning\n\nExercise 2.1, **Rotation Matrix Verification**, teaches you how to mathematically verify rotation representations in 3D space. In robotics, rotations are represented by $3 \\times 3$ matrices belonging to the Special Orthogonal Group $SO(3)$.\n\nBefore you can use a matrix to rotate vectors, you must ensure it does not scale or shear the space. A valid rotation matrix preserves lengths, angles, and orientation.\n\n### Intuition\n\nEvery column (and row) of a rotation matrix represents a coordinate axis of a rotated frame projected onto the reference frame. These axes must be:\n- Unit vectors (length = 1).\n- Mutually orthogonal (perpendicular to each other, dot product = 0).\n- Right-handed (the cross product of the first two axes yields the third axis, which is enforced by the determinant being +1).\n\n### Go mental model\n\n- In Go, a 3D matrix is represented naturally by a nested array `[3][3]float64`.\n- Floating-point calculations can introduce tiny errors (e.g., `0.9999999999999` instead of `1.0`). Always compare values using an absolute delta difference, e.g., `math.Abs(a - b) < 1e-5`, rather than `a == b`.",
        "explanation": "### What you are learning\n\nExercise 2.1, **Rotation Matrix Verification**, teaches you how to mathematically verify rotation representations in 3D space. In robotics, rotations are represented by $3 \\times 3$ matrices belonging to the Special Orthogonal Group $SO(3)$.\n\nBefore you can use a matrix to rotate vectors, you must ensure it does not scale or shear the space. A valid rotation matrix preserves lengths, angles, and orientation.\n\n### Intuition\n\nEvery column (and row) of a rotation matrix represents a coordinate axis of a rotated frame projected onto the reference frame. These axes must be:\n- Unit vectors (length = 1).\n- Mutually orthogonal (perpendicular to each other, dot product = 0).\n- Right-handed (the cross product of the first two axes yields the third axis, which is enforced by the determinant being +1).\n\n### Go mental model\n\n- In Go, a 3D matrix is represented naturally by a nested array `[3][3]float64`.\n- Floating-point calculations can introduce tiny errors (e.g., `0.9999999999999` instead of `1.0`). Always compare values using an absolute delta difference, e.g., `math.Abs(a - b) < 1e-5`, rather than `a == b`.",
        "howItWorks": "### How it works\n\nA complete check involves two main steps:\n\n1. **Check Orthogonality ($R^T R = I$):**\n   Compute the product of $R^T$ (transpose of $R$) and $R$. Every element in the resulting matrix should be close to the Identity matrix $I$.\n   - Diagonal elements: $I_{ii} \\approx 1.0$\n   - Off-diagonal elements: $I_{ij} \\approx 0.0$\n\n2. **Check Determinant ($\\det(R) = 1$):**\n   Compute the determinant of a $3 \\times 3$ matrix using the formula:\n   $$\\det(R) = R_{00}(R_{11}R_{22} - R_{12}R_{21}) - R_{01}(R_{10}R_{22} - R_{12}R_{20}) + R_{02}(R_{10}R_{21} - R_{11}R_{20})$$\n   Check if this value is within `1e-5` of `1.0`.\n\n### Debugging Lens\nIf your code returns `false` unexpectedly, print out the computed determinant and the elements of the computed identity matrix to see which constraint was violated.",
        "syntax": "### Syntax you need\n\nImport the `math` package for floating-point helpers:\n```go\nimport \"math\"\n```\n\nIterating over elements and computing absolute differences:\n```go\nif math.Abs(val - expected) > 1e-5 {\n    return false\n}\n```",
        "solve": "### Solve path for Exercise 2.1\n\n1. Write a helper function to compute the transpose of a 3x3 matrix.\n2. Write a helper function to multiply two 3x3 matrices.\n3. Compute $M = R^T R$ and verify that $M$ is within `1e-5` tolerance of the Identity matrix $I$.\n4. Compute the determinant of $R$ and check that $\\det(R) \\approx 1.0$.\n5. Return `true` only if both conditions are satisfied.",
        "approach": "### Solve path for Exercise 2.1\n\n1. Write a helper function to compute the transpose of a 3x3 matrix.\n2. Write a helper function to multiply two 3x3 matrices.\n3. Compute $M = R^T R$ and verify that $M$ is within `1e-5` tolerance of the Identity matrix $I$.\n4. Compute the determinant of $R$ and check that $\\det(R) \\approx 1.0$.\n5. Return `true` only if both conditions are satisfied.",
        "pitfalls": [
            "Using exact float comparison (==) which fails due to precision limits.",
            "Incorrect indexing for the determinant formula.",
            "Forgetting to check the orthogonality condition and only checking the determinant."
        ],
        "hints": [
            "Use math.Abs(value - target) < 1e-5 for all numeric comparisons.",
            "For orthogonality, compute R^T * R and check if it equals the identity matrix.",
            "The determinant formula for 3x3 uses three 2x2 determinants."
        ],
        "starterCode": "package main\n\nimport \"math\"\n\nfunc Solve(R [3][3]float64) bool {\n    // TODO: Verify SO(3) conditions\n    return false\n}",
        "solutionCode": "package main\n\nimport \"math\"\n\nfunc Solve(R [3][3]float64) bool {\n    // 1. Check determinant\n    det := R[0][0]*(R[1][1]*R[2][2] - R[1][2]*R[2][1]) - \n           R[0][1]*(R[1][0]*R[2][2] - R[1][2]*R[2][0]) + \n           R[0][2]*(R[1][0]*R[2][1] - R[1][1]*R[2][0])\n    if math.Abs(det - 1.0) > 1e-5 {\n        return false\n    }\n\n    // 2. Check R^T * R == I\n    var RTR [3][3]float64\n    for i := 0; i < 3; i++ {\n        for j := 0; j < 3; j++ {\n            sum := 0.0\n            for k := 0; k < 3; k++ {\n                sum += R[k][i] * R[k][j] // R[k][i] is R^T[i][k]\n            }\n            RTR[i][j] = sum\n        }\n    }\n\n    for i := 0; i < 3; i++ {\n        for j := 0; j < 3; j++ {\n            expected := 0.0\n            if i == j {\n                expected = 1.0\n            }\n            if math.Abs(RTR[i][j] - expected) > 1e-5 {\n                return false\n            }\n        }\n    }\n\n    return true\n}",
        "testCode": "func main() {\n    // Test Case 1: Identity Matrix (Valid)\n    I := [3][3]float64{\n        {1.0, 0.0, 0.0},\n        {0.0, 1.0, 0.0},\n        {0.0, 0.0, 1.0},\n    }\n    assertEqual(Solve(I), true)\n\n    // Test Case 2: 90 deg rotation around Z axis (Valid)\n    Rz := [3][3]float64{\n        {0.0, -1.0, 0.0},\n        {1.0, 0.0, 0.0},\n        {0.0, 0.0, 1.0},\n    }\n    assertEqual(Solve(Rz), true)\n\n    // Test Case 3: Scaling Matrix (Invalid)\n    Scale := [3][3]float64{\n        {2.0, 0.0, 0.0},\n        {0.0, 2.0, 0.0},\n        {0.0, 0.0, 2.0},\n    }\n    assertEqual(Solve(Scale), false)\n\n    // Test Case 4: Left-handed rotation (Invalid)\n    Left := [3][3]float64{\n        {1.0, 0.0, 0.0},\n        {0.0, 1.0, 0.0},\n        {0.0, 0.0, -1.0},\n    }\n    assertEqual(Solve(Left), false)\n}",
        "exerciseMode": "judge",
        "verifier": "local-tests",
        "examples": [
            {
                "input": "R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]",
                "output": "true"
            },
            {
                "input": "R = [[2, 0, 0], [0, 2, 0], [0, 0, 2]]",
                "output": "false"
            }
        ]
    },
    {
        "id": "exercise-2-2",
        "number": 2,
        "title": "Exercise 2.2: Skew-Symmetric Matrix of a 3-Vector",
        "chapter": "ch2",
        "difficulty": "Judgeable",
        "tags": ["vector", "matrix", "skew-symmetric"],
        "statement": "Map a 3D angular velocity vector to its 3x3 skew-symmetric matrix representation.",
        "problemText": "Write a function `Solve(omega [3]float64) [3][3]float64` that takes a 3-vector $\\omega = [\\omega_1, \\omega_2, \\omega_3]^T$ and returns its skew-symmetric representation $[\\omega] \\in so(3)$.\n\n### Skew-Symmetric Mapping:\n$$[\\omega] = \\begin{bmatrix} 0 & -\\omega_3 & \\omega_2 \\\\ \\omega_3 & 0 & -\\omega_1 \\\\ -\\omega_2 & \\omega_1 & 0 \\end{bmatrix}$$",
        "lessonTitle": "Intuitive Explanation",
        "lesson": "### What you are learning\n\nExercise 2.2, **Skew-Symmetric Matrix**, introduces the mathematical mapping between a 3D vector and its skew-symmetric matrix. In robotics, this map is fundamental for calculating cross products and representing infinitesimal rotations (Lie algebra $so(3)$).\n\n### Intuition\n\nIn linear algebra, the cross product of two vectors $a \\times b$ can be written as a matrix-vector multiplication $[a]b$. The matrix $[a]$ is the skew-symmetric matrix of $a$.\n\nIn rotation kinematics, skew-symmetric matrices represent angular velocities. If a body rotates with angular velocity $\\omega$, the velocity of a point on the body at position $p$ is $v = \\omega \\times p = [\\omega]p$.\n\n### Go mental model\n\n- The input is a fixed-size array `[3]float64` and the output is a 2D array `[3][3]float64`.\n- This is a straightforward indexing task. There is no complex arithmetic; you just place elements into their designated coordinate locations and fill the diagonal with zeros.",
        "explanation": "### What you are learning\n\nExercise 2.2, **Skew-Symmetric Matrix**, introduces the mathematical mapping between a 3D vector and its skew-symmetric matrix. In robotics, this map is fundamental for calculating cross products and representing infinitesimal rotations (Lie algebra $so(3)$).\n\n### Intuition\n\nIn linear algebra, the cross product of two vectors $a \\times b$ can be written as a matrix-vector multiplication $[a]b$. The matrix $[a]$ is the skew-symmetric matrix of $a$.\n\nIn rotation kinematics, skew-symmetric matrices represent angular velocities. If a body rotates with angular velocity $\\omega$, the velocity of a point on the body at position $p$ is $v = \\omega \\times p = [\\omega]p$.\n\n### Go mental model\n\n- The input is a fixed-size array `[3]float64` and the output is a 2D array `[3][3]float64`.\n- This is a straightforward indexing task. There is no complex arithmetic; you just place elements into their designated coordinate locations and fill the diagonal with zeros.",
        "howItWorks": "### How it works\n\nConstruct the matrix element by element:\n- $[\\omega]_{0,0} = [\\omega]_{1,1} = [\\omega]_{2,2} = 0$\n- $[\\omega]_{0,1} = -\\omega_2$, $[\\omega]_{0,2} = \\omega_1$\n- $[\\omega]_{1,0} = \\omega_2$, $[\\omega]_{1,2} = -\\omega_0$\n- $[\\omega]_{2,0} = -\\omega_1$, $[\\omega]_{2,1} = \\omega_0$\n\nWait, make sure you double-check 0-based index maps compared to math indices:\n- $\\omega_1$ is `omega[0]`\n- $\\omega_2$ is `omega[1]`\n- $\\omega_3$ is `omega[2]`",
        "syntax": "### Syntax you need\n\nCreating and initializing a nested array in Go:\n```go\nvar mat [3][3]float64\nmat[0][1] = -omega[2]\n```",
        "solve": "### Solve path for Exercise 2.2\n\n1. Initialize a empty 3x3 float64 matrix.\n2. Set the diagonal elements to 0.0.\n3. Map `omega[0]` ($\\omega_1$), `omega[1]` ($\\omega_2$), and `omega[2]` ($\\omega_3$) to their appropriate positions in the matrix with correct signs.\n4. Return the constructed matrix.",
        "approach": "### Solve path for Exercise 2.2\n\n1. Initialize a empty 3x3 float64 matrix.\n2. Set the diagonal elements to 0.0.\n3. Map `omega[0]` ($\\omega_1$), `omega[1]` ($\\omega_2$), and `omega[2]` ($\\omega_3$) to their appropriate positions in the matrix with correct signs.\n4. Return the constructed matrix.",
        "pitfalls": [
            "Mixing up 1-based math indexes (1, 2, 3) with 0-based Go indexes (0, 1, 2).",
            "Swapping the sign of off-diagonal elements."
        ],
        "hints": [
            "omega[0] represents w1, omega[1] is w2, and omega[2] is w3.",
            "The diagonal elements R[0][0], R[1][1], R[2][2] must all be exactly 0.0."
        ],
        "starterCode": "package main\n\nfunc Solve(omega [3]float64) [3][3]float64 {\n    var mat [3][3]float64\n    // TODO: Compute skew-symmetric matrix\n    return mat\n}",
        "solutionCode": "package main\n\nfunc Solve(omega [3]float64) [3][3]float64 {\n    var mat [3][3]float64\n    \n    // Row 0\n    mat[0][0] = 0.0\n    mat[0][1] = -omega[2]\n    mat[0][2] = omega[1]\n    \n    // Row 1\n    mat[1][0] = omega[2]\n    mat[1][1] = 0.0\n    mat[1][2] = -omega[0]\n    \n    // Row 2\n    mat[2][0] = -omega[1]\n    mat[2][1] = omega[0]\n    mat[2][2] = 0.0\n    \n    return mat\n}",
        "testCode": "func main() {\n    // Test Case 1: Simple vector [1, 2, 3]\n    omega := [3]float64{1.0, 2.0, 3.0}\n    expected := [3][3]float64{\n        {0.0, -3.0, 2.0},\n        {3.0, 0.0, -1.0},\n        {-2.0, 1.0, 0.0},\n    }\n    assertEqual(Solve(omega), expected)\n\n    // Test Case 2: Zero vector\n    zero := [3]float64{0.0, 0.0, 0.0}\n    expectedZero := [3][3]float64{\n        {0.0, 0.0, 0.0},\n        {0.0, 0.0, 0.0},\n        {0.0, 0.0, 0.0},\n    }\n    assertEqual(Solve(zero), expectedZero)\n}",
        "exerciseMode": "judge",
        "verifier": "local-tests",
        "examples": [
            {
                "input": "omega = [1, 2, 3]",
                "output": "[[0, -3, 2], [3, 0, -1], [-2, 1, 0]]"
            }
        ]
    },
    {
        "id": "exercise-4-1",
        "number": 3,
        "title": "Exercise 4.1: 2R Planar Robot PoE Kinematics",
        "chapter": "ch4",
        "difficulty": "Judgeable",
        "tags": ["robotics", "kinematics", "poe"],
        "statement": "Calculate the end-effector position of a 2R planar robot using the Product of Exponentials (PoE) formula.",
        "problemText": "Calculate the end-effector position $(x, y)$ of a planar 2-link revolute joint (2R) robot using the Product of Exponentials (PoE) formula.\n\n### System Parameters:\n- Link lengths: $L_1$ and $L_2$.\n- Both joints rotate in the 2D plane.\n- Home configuration $M$ (when joint angles are zero): the robot lies fully extended along the positive X-axis. The end-effector frame is at distance $L_1 + L_2$ from the origin, oriented parallel to the reference frame.\n- Joint 1 is located at the origin $(0, 0)$. Joint 2 is located at $(L_1, 0)$.\n\nWrite a function `Solve(theta1, theta2, L1, L2 float64) [2]float64` that returns the final $(x, y)$ position of the end-effector.",
        "lessonTitle": "Intuitive Explanation",
        "lesson": "### What you are learning\n\nExercise 4.1 teaches you the **Product of Exponentials (PoE)** formulation for forward kinematics. While standard DH parameters are popular, PoE is mathematically cleaner and avoids singularities by describing joints using twists relative to a single fixed base frame.\n\n### Intuition\n\nUnder the PoE formula, a robot in its 'Home' configuration has its end-effector at some position/orientation matrix $M$. Each joint $i$ represents a helical axis (twist) $S_i$ in space.\n\nWhen we rotate joint 1 by $\\theta_1$ and joint 2 by $\\theta_2$, the end-effector moves according to successive matrix exponentials:\n$$T(\\theta) = e^{[S_1]\\theta_1} e^{[S_2]\\theta_2} M$$\n\nFor a simple 2R planar robot, we can compute the coordinates by applying successive rotations to the link vectors relative to the origin base frame.\n\n### Go mental model\n\n- The input gives the joint angles and the physical link lengths.\n- The output is an array of size 2: `[2]float64` representing the $(x, y)$ coordinates.\n- Use the `math.Sin` and `math.Cos` functions to rotate vectors. Joint 1 affects both links, while joint 2 only affects link 2 relative to link 1's orientation.",
        "explanation": "### What you are learning\n\nExercise 4.1 teaches you the **Product of Exponentials (PoE)** formulation for forward kinematics. While standard DH parameters are popular, PoE is mathematically cleaner and avoids singularities by describing joints using twists relative to a single fixed base frame.\n\n### Intuition\n\nUnder the PoE formula, a robot in its 'Home' configuration has its end-effector at some position/orientation matrix $M$. Each joint $i$ represents a helical axis (twist) $S_i$ in space.\n\nWhen we rotate joint 1 by $\\theta_1$ and joint 2 by $\\theta_2$, the end-effector moves according to successive matrix exponentials:\n$$T(\\theta) = e^{[S_1]\\theta_1} e^{[S_2]\\theta_2} M$$\n\nFor a simple 2R planar robot, we can compute the coordinates by applying successive rotations to the link vectors relative to the origin base frame.\n\n### Go mental model\n\n- The input gives the joint angles and the physical link lengths.\n- The output is an array of size 2: `[2]float64` representing the $(x, y)$ coordinates.\n- Use the `math.Sin` and `math.Cos` functions to rotate vectors. Joint 1 affects both links, while joint 2 only affects link 2 relative to link 1's orientation.",
        "howItWorks": "### How it works\n\nFor a 2R planar robot, joint 1 is at the base. It rotates the entire arm by angle $\\theta_1$.\nJoint 2 is at distance $L_1$ along the arm. It rotates the second link by angle $\\theta_2$ relative to the first link.\n\nThe global orientation of link 1 is $\\theta_1$.\nThe global orientation of link 2 is $\\theta_1 + \\theta_2$.\n\nThus, the position of the joint 2 is:\n$$x_2 = L_1 \\cos(\\theta_1)$$\n$$y_2 = L_1 \\sin(\\theta_1)$$\n\nAnd the end-effector position relative to joint 2 is:\n$$x_{ee} = x_2 + L_2 \\cos(\\theta_1 + \\theta_2)$$\n$$y_{ee} = y_2 + L_2 \\sin(\\theta_1 + \\theta_2)$$\n\nThis simple trigonometric relationship is the closed-form projection of the PoE formula for planar revolute chains.",
        "syntax": "### Syntax you need\n\nTrigonometric operations in Go:\n```go\nimport \"math\"\n\nx := L1 * math.Cos(theta1)\ny := L1 * math.Sin(theta1)\n```",
        "solve": "### Solve path for Exercise 4.1\n\n1. Calculate the position of Joint 2: $x_1 = L_1 \\cos(\\theta_1)$ and $y_1 = L_1 \\sin(\\theta_1)$.\n2. Calculate the end-effector position relative to Joint 2: $x_2 = L_2 \\cos(\\theta_1 + \\theta_2)$ and $y_2 = L_2 \\sin(\\theta_1 + \\theta_2)$.\n3. Sum these two components to get the total $x$ and $y$.\n4. Return a `[2]float64` array containing $[x, y]$.",
        "approach": "### Solve path for Exercise 4.1\n\n1. Calculate the position of Joint 2: $x_1 = L_1 \\cos(\\theta_1)$ and $y_1 = L_1 \\sin(\\theta_1)$.\n2. Calculate the end-effector position relative to Joint 2: $x_2 = L_2 \\cos(\\theta_1 + \\theta_2)$ and $y_2 = L_2 \\sin(\\theta_1 + \\theta_2)$.\n3. Sum these two components to get the total $x$ and $y$.\n4. Return a `[2]float64` array containing $[x, y]$.",
        "pitfalls": [
            "Using degrees instead of radians. Go's math functions expect joint angles in radians.",
            "Incorrectly calculating the second link orientation (forgetting that joint 2 angle is relative to link 1, so the absolute angle is theta1 + theta2)."
        ],
        "hints": [
            "Go's math.Cos and math.Sin expect angles in radians.",
            "Link 2 absolute angle in the world frame is theta1 + theta2.",
            "Add the coordinate vector of link 1 to the coordinate vector of link 2 to get the end effector."
        ],
        "starterCode": "package main\n\nimport \"math\"\n\nfunc Solve(theta1, theta2, L1, L2 float64) [2]float64 {\n    // TODO: Compute planar kinematics\n    return [2]float64{0.0, 0.0}\n}",
        "solutionCode": "package main\n\nimport \"math\"\n\nfunc Solve(theta1, theta2, L1, L2 float64) [2]float64 {\n    x := L1*math.Cos(theta1) + L2*math.Cos(theta1+theta2)\n    y := L1*math.Sin(theta1) + L2*math.Sin(theta1+theta2)\n    return [2]float64{x, y}\n}",
        "testCode": "import \"math\"\n\nfunc assertNear(got, want [2]float64) {\n    if math.Abs(got[0]-want[0]) > 1e-5 || math.Abs(got[1]-want[1]) > 1e-5 {\n        panic(nil) // Trigger failure\n    }\n}\n\nfunc main() {\n    // Home configuration: angles = 0\n    assertNear(Solve(0, 0, 1.0, 1.0), [2]float64{2.0, 0.0})\n\n    // 90 degree turn on joint 1\n    assertNear(Solve(math.Pi/2, 0, 1.0, 1.0), [2]float64{0.0, 2.0})\n\n    // Joint 1 = 90 deg, Joint 2 = -90 deg (folding back)\n    assertNear(Solve(math.Pi/2, -math.Pi/2, 1.0, 1.0), [2]float64{1.0, 1.0})\n}",
        "exerciseMode": "judge",
        "verifier": "local-tests",
        "examples": [
            {
                "input": "theta1 = 0, theta2 = 0, L1 = 1, L2 = 1",
                "output": "[2, 0]"
            },
            {
                "input": "theta1 = 1.5708, theta2 = 0, L1 = 1, L2 = 1",
                "output": "[0, 2]"
            }
        ]
    }
]

# =====================================================================
# PDF Table of Contents Extraction Helper
# =====================================================================

def extract_toc(pdf_path: str) -> str:
    """Extract pages 5 to 15 which typically contain the Table of Contents."""
    from pypdf import PdfReader
    try:
        reader = PdfReader(pdf_path)
        toc_text = []
        # Usually TOC is in the first 15 pages
        for i in range(4, min(15, len(reader.pages))):
            toc_text.append(reader.pages[i].extract_text())
        return "\n".join(toc_text)
    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        return ""

# =====================================================================
# Main Pipeline Executable
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Transform any textbook PDF into a dynamically rebranded practice catalog for the agentic learning platform."
    )
    parser.add_argument("--pdf", type=str, default="MR.pdf", help="Path to the book PDF file (e.g., MR.pdf)")
    parser.add_argument("--out", type=str, default="data/problems.json", help="Path to save the generated JSON catalog")
    parser.add_argument("--dry-run", action="store_true", help="Generate a high-quality mock robotics catalog without hitting the Gemini API")
    
    args = parser.parse_args()

    print("====================================================================")
    print("      AGENTIC TEXTBOOK INGESTION PIPELINE (PDF -> PROBLEMS.JSON)    ")
    print("====================================================================")
    
    # Check if PDF exists
    pdf_exists = os.path.exists(args.pdf)
    if not pdf_exists and not args.dry_run:
        print(f"\n[!] Warning: '{args.pdf}' not found in the current directory.")
        print("To run the real pipeline, please place the book PDF in this directory.")
        print("Falling back to --dry-run mode to generate a high-quality robotics catalog instantly.")
        args.dry_run = True

    # 1. Handle Dry Run / Mock Mode
    if args.dry_run:
        print("\n[*] Initializing Dry-Run / Mock Ingestion Mode...")
        print(f"[*] Packaging Modern Robotics catalog for language: '{MOCK_METADATA['language']}'")
        
        store_data = {
            "metadata": MOCK_METADATA,
            "chapters": MOCK_CHAPTERS,
            "problems": MOCK_PROBLEMS
        }
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        
        # Write catalog
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(store_data, f, indent=2, ensure_ascii=False)
            
        print(f"\n[✓] Success! Beautifully structured catalog written to: {args.out}")
        print(f"    - Dynamic title: {MOCK_METADATA['title']}")
        print(f"    - Chapters: {len(MOCK_CHAPTERS)}")
        print(f"    - Coding exercises: {len(MOCK_PROBLEMS)}")
        print("\nTo see the dynamic rebranding:")
        print("  1. Start backend: cd backend && go run .")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. View in browser! The header will dynamically rebrand itself to 'Modern Robotics'!")
        return

    # 2. Real API Generation Mode
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[!] Error: GEMINI_API_KEY environment variable is not set.")
        print("Please set it in your terminal, or create a '.env' file containing:")
        print("  GEMINI_API_KEY=your_gemini_api_key")
        print("\nAlternatively, run with --dry-run to generate the catalog instantly.")
        sys.exit(1)

    print(f"\n[*] Reading PDF content from '{args.pdf}'...")
    toc_content = extract_toc(args.pdf)
    if not toc_content:
        print("[!] Error: Could not extract Table of Contents from PDF.")
        sys.exit(1)

    print(f"[✓] Extracted Table of Contents successfully ({len(toc_content)} characters).")

    # Import GenAI SDK
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("[!] Error: google-genai package is not installed.")
        print("Please run this script using `uv run scripts/book_to_problems.py` which installs it automatically.")
        sys.exit(1)

    print("\n[*] Contacting Gemini API (gemini-2.5-flash) to structure Chapters...")
    client = genai.Client()

    chapter_prompt = f"""
You are a senior Robotics & Curriculum Designer.
Given the Table of Contents text extracted from a robotics textbook, analyze it and organize it into a list of 3-5 core chapters suitable for a self-hosted coding platform.
Each chapter should have a clear id, title, and description.

Table of Contents:
{toc_content}
"""

    try:
        response_chapters = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=chapter_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ChaptersList,
            ),
        )
        chapters_data = json.loads(response_chapters.text)["chapters"]
        print(f"[✓] Structured {len(chapters_data)} chapters successfully!")
    except Exception as e:
        print(f"[!] Error calling Gemini API: {e}")
        sys.exit(1)

    # Generate problems for each chapter
    all_problems = []
    problem_count = 1

    for ch in chapters_data:
        print(f"\n[*] Generating Go exercises for Chapter: '{ch['title']}'...")
        
        problem_prompt = f"""
You are an expert Robot Systems Engineer and Go Developer.
Your task is to generate 2 highly educational 'Judgeable' coding exercises in Go for the chapter '{ch['title']}' ({ch['description']}) from a robotics textbook.

The coding exercises MUST:
1. Focus on implementing real math formulas, matrices, or algorithms of this chapter in Go.
2. Be fully compatible with Go standard library (no custom dependencies like gonum). Use nested arrays (e.g. `[3][3]float64`) or slices.
3. Be fully judgeable via standard comparisons.
4. Have starter code, a complete correct solution code, and a solid test suite (`testCode`) with `func main()` calling `assertEqual(got, want)` or custom delta checks for floats.
5. Have detailed markdown explanations, syntax patterns, progressive hints, and common pitfalls.
6. The verifier type must be 'local-tests' and exerciseMode must be 'judge'.

Format the response according to the provided JSON schema. Ensure all Go code block contents are properly escaped strings in JSON.
"""

        try:
            response_problems = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=problem_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ProblemsList,
                ),
            )
            problems_list = json.loads(response_problems.text)["problems"]
            
            # Postprocess and assign sequential numbers
            for p in problems_list:
                p["chapter"] = ch["id"]
                p["number"] = problem_count
                p["lessonTitle"] = "Intuitive Explanation"
                p["lesson"] = p["explanation"]
                p["approach"] = p["solve"]
                problem_count += 1
                all_problems.append(p)
                
            print(f"  [✓] Generated {len(problems_list)} exercises.")
        except Exception as e:
            print(f"  [!] Skipped chapter due to API error: {e}")

    # Build final Store
    store_data = {
        "metadata": {
            "title": "Modern Robotics",
            "subtitle": "Mechanics, Planning, and Control in Go",
            "language": "go"
        },
        "chapters": chapters_data,
        "problems": all_problems
    }

    # Save to file
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(store_data, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Succeed! Fully generated dynamic robotics catalog written to: {args.out}")
    print(f"    - Chapters: {len(chapters_data)}")
    print(f"    - Exercises: {len(all_problems)}")

if __name__ == "__main__":
    main()
