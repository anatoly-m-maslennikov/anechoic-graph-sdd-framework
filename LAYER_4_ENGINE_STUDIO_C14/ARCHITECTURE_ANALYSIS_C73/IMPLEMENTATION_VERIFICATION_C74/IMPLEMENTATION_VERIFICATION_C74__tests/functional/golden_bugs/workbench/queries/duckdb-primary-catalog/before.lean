-- Source SQL: select table_type from information_schema.tables where table_schema = 'main' and table_name = 'native_references'
def catalogFilter : Bool := false
def leaked (attachedMatch : Bool) : Bool := attachedMatch && !catalogFilter
#eval leaked true
