# Proposed CFEL item owners

User approved individual CFEL Subjects. Semantic labels below remain proposed unless otherwise noted; no Category carrier is introduced.

| Item | Form | Active Subject |
|---|---|---|
| `+` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Addition` |
| `==` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Required Value` |
| `=` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Equality` |
| `>=` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Greater Than or Equal` |
| `>` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Greater Than` |
| `<=` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Less Than or Equal` |
| `<` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Less Than` |
| `!=` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Inequality` |
| `()` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Grouping` |
| `*` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Immediate Property Selection` |
| `**` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Recursive Property Selection` |
| `$ participant selection` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Participant Binding` |
| `[] Format` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Format` |
| `<> Model reference` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Model Reference` |
| `in` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Membership` |
| `not in` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Membership` |
| `!() delivery exclusion` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Delivery Exclusion` |
| `>> delivery` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Delivery` |
| `?== default` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Default` |
| `AND` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Conjunction` |
| `OR` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Disjunction` |
| `FOR EACH` | Construct Declaration | `ANECHOIC_MODEL/CFEL/Construct//Universal Quantification` |
| `IF / THEN` | Construct Declaration | `ANECHOIC_MODEL/CFEL/Construct//Conditional` |
| `IF / THEN / ELSE` | Construct Declaration | `ANECHOIC_MODEL/CFEL/Construct//Conditional` |
| `((Relation))` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Relation Direction` |
| `<((Relation))` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Relation Direction` |
| `HAS_ALLOWED_VALUE :=` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//HAS_ALLOWED_VALUE` |
| `HAS_VALUE_CONSTRAINT ::` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//HAS_VALUE_CONSTRAINT` |
| `IS_PROPERTY_OF .` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//IS_PROPERTY_OF` |
| `HAS_NARROWER //` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//HAS_NARROWER` |
| `CONTAINS /` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//CONTAINS` |
| `IS_CONTAINED_BY +>` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//IS_CONTAINED_BY` |
| `HAS_CLASSIFICATION >| and |<` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//HAS_CLASSIFICATION` |
| `HAS_INVERSE <-->` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//HAS_INVERSE` |
| `qualified Subject :=` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//HAS_ALLOWED_VALUE` |
| `VALUES` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//VALUES` |
| `COUNT` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//COUNT` |
| `MAX` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//MAX` |
| `LOOKUP` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//LOOKUP` |
| `FENCED_LABELS` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//FENCED_LABELS` |
| `alias` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//alias` |
| `UNIQUE` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//UNIQUE` |
| `DETERMINES` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//DETERMINES` |
| `DISTINCT` | Function Declaration | `ANECHOIC_MODEL/CFEL/Function//COUNT` |
| `;` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Expression Separator` |
| `# model / # instances` | retained generic CFEL language Declaration | `ANECHOIC_MODEL/CFEL` |
| `: FOR EACH delimiter` | Construct Declaration | `ANECHOIC_MODEL/CFEL/Construct//Universal Quantification` |
| `| HAV alternatives` | Relation Declaration | `ANECHOIC_MODEL/CFEL/Relation//HAS_ALLOWED_VALUE` |
| `, in list` | Operator Declaration | `ANECHOIC_MODEL/CFEL/Operator//Membership` |

FOR EACH and Conditional are multi-expression Constructs. ELSE behavior and scope remain pending. DISTINCT and punctuation are mapped to their owning item; comments use the retained whole-language Declaration.
