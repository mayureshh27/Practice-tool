import type { Domain, WorkflowTemplate, Artifact } from '../workspaceTypes';

export const INITIAL_DOMAINS: Domain[] = [
  {
    id: 'robotics',
    name: 'Robotics',
    pinned: true,
    subjects: [
      {
        id: 'modern-robotics',
        name: 'Modern Robotics',
        description: 'Master kinematics, rigid body motions, dynamics, and planning of robotic manipulators.',
        instructions: 'Emphasize screw theory, exponential coordinate representations, and homogeneous transformations.',
        memory: 'Mayuresh is a Computer Science student in India (AI and Data Science specialization, 8/10 GPA, graduating 2027). Transitioning to a robotics/ML engineer. Aiming for top-10 MS programs.',
        pinned: true,
        chapters: [
          {
            id: 'c2',
            name: 'Chapter 2: Configuration Space',
            description: 'Degrees of freedom, Grubler\'s formula, configuration space topology, task space vs C-space.',
            instructions: 'Check planar vs spatial degrees of freedom factors and C-space dimensional topology.',
            memory: 'Focus on screw coordinate systems and spatial tree joints.',
            topics: [
              { id: 'deg-freedom', name: 'Degrees of Freedom', lastMessage: 'Completed 1 hour ago', pinned: true },
              { id: 'grubler-formula', name: "Grubler's Formula", lastMessage: 'Needs practice' },
              { id: 'cspace-topology', name: 'Configuration Space Topology', lastMessage: 'Solved 2 days ago' }
            ]
          },
          {
            id: 'c3',
            name: 'Chapter 3: Rigid-Body Motions',
            description: 'Rotation matrices, SO(3), exponential coordinates of rotation, skew-symmetric matrices, Rodrigues\' formula.',
            instructions: 'Focus on Rodrigues\' formula and 3D coordinate transformations.',
            memory: 'Rigid body rotations and SO(3) coordinate frames.',
            topics: [
              { id: 'rot-matrices', name: 'Rotation Matrices', lastMessage: 'Not started' },
              { id: 'hom-transforms', name: 'Homogeneous Transformations', lastMessage: 'Not started' }
            ]
          }
        ],
        resources: [
          { id: 'res-pdf', name: 'Modern_Robotics_Kinematics.pdf', lines: 14500, fileType: 'PDF' },
          { id: 'res-deriv', name: 'Screw_Theory_Derivations.md', lines: 320, fileType: 'MD' },
          { id: 'res-lib', name: 'robotics_math.js', lines: 750, fileType: 'JS' }
        ]
      },
      {
        id: 'cmu-mrsd',
        name: 'CMU MRSD Prep',
        description: 'Preparation exercises for CMU Master of Robotic Systems Development curriculum.',
        instructions: 'Focus on state-space representations, PID control loop feedback stability, and integral windup.',
        memory: 'CS AI/Data Science student preparing for CMU MRSD controls courses.',
        chapters: [
          {
            id: 'ctrl-th',
            name: 'Control Theory',
            description: 'Feedback loop structures, proportional integral derivative variables, transfer functions.',
            instructions: 'Emphasize standard PID integral windup pitfalls.',
            memory: 'PID feedforward and feedback loop gains.',
            topics: [
              { id: 'pid-tuning', name: 'PID Feedback Control Loop', lastMessage: 'Draft ready' }
            ]
          }
        ],
        resources: [
          { id: 'res-ctrl', name: 'PID_Controller_Design.pdf', lines: 4500, fileType: 'PDF' }
        ]
      }
    ]
  },
  {
    id: 'perception',
    name: 'Perception',
    subjects: [
      {
        id: 'computer-vision',
        name: 'Computer Vision',
        description: 'Mathematical operations for digital image filters, edge extraction, and descriptors.',
        instructions: 'Focus on pixel convolution kernels, Sobel derivatives, and SIFT descriptor mappings.',
        memory: 'Perception and sensor fusion concepts for self driving perception pipelines.',
        chapters: [
          {
            id: 'filters',
            name: 'Image Filters & Operators',
            description: 'Gaussian blurs, kernel convolutions, Sobel derivatives, and gradient magnitude.',
            instructions: 'Derive edge gradient magnitude equations manually.',
            memory: 'Pixel convolutions and Gaussian kernel convolutions.',
            topics: [
              { id: 'gaussian-blur', name: 'Gaussian Filter Derivation', lastMessage: 'Not started' },
              { id: 'sobel-edge', name: 'Sobel Edge Kernel Convolution', lastMessage: 'Not started' }
            ]
          }
        ],
        resources: [
          { id: 'res-cv', name: 'Computer_Vision_Algorithms.md', lines: 1100, fileType: 'MD' }
        ]
      }
    ]
  },
  {
    id: 'go-programming',
    name: 'Go Programming',
    pinned: true,
    subjects: [
      {
        id: 'go-fundamentals',
        name: 'Go Fundamentals',
        description: 'Learn the fundamentals of Go, including basic types, variables, control flow, functions, slices, maps, and concurrency.',
        instructions: 'Focus on pointers, array slice internals, maps, goroutines, and channels.',
        memory: 'CS AI/Data Science student learning systems programming and concurrency in Go.',
        pinned: true,
        chapters: [
          {
            id: 'go-basics',
            name: 'Chapter 1: Basics & Functions',
            description: 'Go syntax, basic types, variable declarations, loop constructs, and simple functions.',
            instructions: 'Declare functions with explicit types and explore value vs pointer parameters.',
            memory: 'Learn clean, idiomatic variable declaration blocks in Go.',
            topics: [
              { id: 'hello-world', name: 'Hello World', lastMessage: 'Draft ready', pinned: true },
              { id: 'fizzbuzz', name: 'FizzBuzz Game', lastMessage: 'Not started' }
            ]
          }
        ],
        resources: [
          { id: 'go-quickstart', name: 'Go_Basics_Quickstart.md', lines: 180, fileType: 'MD' },
          { id: 'go-spec', name: 'Go_Language_Specification.pdf', lines: 8400, fileType: 'PDF' }
        ]
      }
    ]
  }
];

export const INITIAL_WORKFLOWS: WorkflowTemplate[] = [
  {
    id: 'wf-practice',
    name: 'Practice Exercises Generator',
    targetType: 'Exercise Pack',
    description: 'Generates structured practice problems and coding tests based on textbook chapters and resources.',
    evalGates: 3,
    lastRun: '2 hours ago'
  },
  {
    id: 'wf-summary',
    name: 'Concept Synthesizer',
    targetType: 'Summary',
    description: 'Synthesizes key formulas, coordinate definitions, and structural derivations from loaded PDF files.',
    evalGates: 2,
    lastRun: '1 day ago'
  },
  {
    id: 'wf-quiz',
    name: 'Interactive Diagnostic Quiz',
    targetType: 'Quiz',
    description: 'Generates conceptual multiple choice questions to probe understanding and highlight weak spots.',
    evalGates: 1,
    lastRun: '3 days ago'
  },
  {
    id: 'wf-code-practice',
    name: 'Sandbox Code Practice Solver',
    targetType: 'Practice Solver',
    description: 'Executes compiler runs, runs assert unit tests, parses diagnostics, and saves local completion records.',
    evalGates: 3,
    lastRun: 'Just now'
  }
];

export const INITIAL_ARTIFACTS: Artifact[] = [
  {
    id: 'art-1',
    name: 'Draft Configuration Space Exercise Pack',
    type: 'Exercise Pack',
    status: 'draft',
    domainId: 'robotics',
    subjectId: 'modern-robotics',
    chapterId: 'c2',
    topicId: 't1',
    time: '2 mins ago'
  },
  {
    id: 'art-2',
    name: 'Grubler Formula Derivations',
    type: 'Summary',
    status: 'approved',
    domainId: 'robotics',
    subjectId: 'modern-robotics',
    chapterId: 'c2',
    topicId: 't2',
    time: '1 hour ago'
  },
  {
    id: 'art-3',
    name: 'Coordinate Systems & Homogeneous Quiz',
    type: 'Quiz',
    status: 'reviewed',
    domainId: 'robotics',
    subjectId: 'modern-robotics',
    chapterId: 'c3',
    time: '1 day ago'
  }
];
