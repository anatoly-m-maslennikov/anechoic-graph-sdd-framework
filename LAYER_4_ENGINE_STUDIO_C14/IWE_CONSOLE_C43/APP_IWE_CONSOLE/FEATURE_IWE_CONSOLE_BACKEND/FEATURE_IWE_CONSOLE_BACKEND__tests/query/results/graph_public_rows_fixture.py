"""Expected public graph relation rows."""

PUBLIC_ROWS = [
    [
        ".",
        "A.md",
        "A",
        {
            "CONTAINS": [
                {
                    "kind": "Atom",
                    "reference": "B",
                    "derived": False,
                }
            ]
        },
    ],
    [
        ".",
        "B.md",
        "B",
        {
            "CONTAINS": [
                {
                    "kind": "Atom",
                    "reference": "A",
                    "derived": True,
                },
                {
                    "kind": "Atom",
                    "reference": "C",
                    "derived": False,
                },
            ],
            "DRAFT_LINK": [
                {
                    "kind": "Atom",
                    "reference": "A@2-draft",
                    "derived": False,
                }
            ],
        },
    ],
]
