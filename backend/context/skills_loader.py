# backend/context/skills_loader.py
import tiktoken
from pathlib import Path

PLATFORM_DIR = Path.home() / ".platform"
SKILLS_DIR = PLATFORM_DIR / "skills"

DEFAULT_GLOBAL_SKILL = """# .platform/skills/_global.md
## Tutor identity
You are a Socratic learning partner for an engineering student targeting
CMU MRSD (Robotics Systems Development) Fall 2028.

## Absolute rules
- Never give the direct solution. Guide with a targeted question.
- When code is wrong, point to the specific line, not the fix.
- If the student asks for the answer directly, refuse and ask what they
  have tried and where specifically they are stuck.
- Always end a hint with a question that moves thinking forward.
- Keep hints to 3 sentences maximum.

## Output format
- Hints: prose, no bullet points, end with a question mark.
- Explanations: use ### headings (minimum 4) for outline nav.
- Math: use LaTeX inline $...$ and display $$...$$.
- Code examples: include assert statements, never print-only.

## Hard stops
- Do not reproduce copyrighted text verbatim.
- Do not claim code is correct when tests are failing.
- Do not guess at memory — use only what is explicitly provided.
"""

DEFAULT_LINEAR_ALGEBRA_SKILL = """# .platform/skills/linear_algebra.md
## Linear algebra mental models (inject for chapter: la* or ch2*)

### Vectors
A vector is direction + magnitude, not a list of numbers.
Dot product u·v = |u||v|cos(θ) — measures alignment, not length.
Scalar projection of u onto v = (u·v) / |v| — the shadow u casts on v.
Common mistake: dividing by |v| when the task needs |v|².

### Eigenvalues
An eigenvector of A is unchanged in direction by A — only scaled by λ.
Av = λv. Most vectors get rotated AND scaled. Eigenvectors only scale.
For symmetric matrices (covariance, Laplacian): eigenvalues are real,
eigenvectors orthogonal. This is why PCA works cleanly.
Common mistake: computing eig() without verifying (A - λI)v = 0 by hand.

### Matrix decompositions
SVD: A = UΣVᵀ. U and V are orthogonal rotations. Σ is scaling.
The rank of A equals the number of nonzero singular values.
PCA is SVD on the centred data matrix — the right singular vectors
are principal components.
"""

DEFAULT_KINEMATICS_SKILL = """# .platform/skills/kinematics.md
## Robotics Kinematics & Transforms (inject for chapter: ro* or ch3* or ch4*)

### Rotations and SO(3)
Rotation matrices represent orientation. They are orthogonal: RᵀR = I, det(R) = 1.
Exponential coordinates of rotation: a unit rotation axis ω̂ and angle θ.
Common mistake: using raw Euler angles which suffer from gimbal lock instead of rotation matrices or unit quaternions.

### Homogeneous Transformations and SE(3)
T = [[R, p], [0, 1]]. R is in SO(3), p is position vector.
T⁻¹ = [[Rᵀ, -Rᵀp], [0, 1]]. Not just inverting the components!
Adjoint representation [Ad_T] maps twists from one frame to another.

### Forward Kinematics (DH Parameters)
Denavit-Hartenberg parameters use 4 variables (θ, d, a, α) to map link transformations.
Always align coordinate axes z along joint axes of motion.
"""

def bootstrap_skills():
    """Ensure the skills directory exists and default files are present."""
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    
    global_file = SKILLS_DIR / "_global.md"
    if not global_file.exists():
        global_file.write_text(DEFAULT_GLOBAL_SKILL, encoding="utf-8")
        
    la_file = SKILLS_DIR / "linear_algebra.md"
    if not la_file.exists():
        la_file.write_text(DEFAULT_LINEAR_ALGEBRA_SKILL, encoding="utf-8")
        
    kin_file = SKILLS_DIR / "kinematics.md"
    if not kin_file.exists():
        kin_file.write_text(DEFAULT_KINEMATICS_SKILL, encoding="utf-8")

def count_tokens(text: str, model: str = "gpt-4") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def load_skills(problem_tags: list[str],
                problem_chapter: str,
                token_budget: int = 1500) -> str:
    """
    Load and inject skills files relevant to the current problem.
    Global skill always included. Domain skills matched by chapter prefix or tags.
    Hard token budget prevents bloat.
    """
    bootstrap_skills()
    
    blocks: list[tuple[int, str]] = []  # (priority, text)

    # Global skill: always first (priority 0)
    global_file = SKILLS_DIR / "_global.md"
    if global_file.exists():
        blocks.append((0, global_file.read_text(encoding="utf-8")))

    # Domain skills: match by chapter prefix (la, pr, ro, ch, etc.) or tags
    chapter_prefix = problem_chapter[:3].lower()  # "ch3" -> "ch3" or "la1" -> "la1"
    
    for skill_file in sorted(SKILLS_DIR.glob("*.md")):
        if skill_file.name.startswith("_"):
            continue  # already loaded global
            
        stem = skill_file.stem  # e.g., "linear_algebra" or "kinematics"
        domain_tags = stem.replace("_", " ").split()
        tag_set = set(t.lower() for t in problem_tags)
        
        # Match by tag intersection, chapter prefix (e.g. la1 matches linear_algebra), or filename prefix
        if (any(t in tag_set for t in domain_tags) or 
            chapter_prefix in stem or 
            any(chapter_prefix.startswith(t[:2]) for t in domain_tags)):
            blocks.append((1, skill_file.read_text(encoding="utf-8")))

    # Sort priority then trim to budget
    blocks.sort(key=lambda x: x[0])
    result_parts: list[str] = []
    used = 0
    
    for _, text in blocks:
        cost = count_tokens(text)
        if used + cost <= token_budget:
            result_parts.append(text)
            used += cost
        else:
            # Truncate to fit remaining budget
            remaining = token_budget - used
            if remaining > 200:  # worth including a partial skill
                words = text.split()
                word_limit = int(remaining * 0.75)
                partial = " ".join(words[:word_limit]) + "\n\n[skill truncated due to context budget]"
                result_parts.append(partial)
            break

    return "\n\n---\n\n".join(result_parts)
