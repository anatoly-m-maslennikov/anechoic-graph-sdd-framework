-- Source SQL: select table_type from information_schema.tables where table_catalog = current_database() and table_schema = 'main' and table_name = 'native_references'
def catalogFilter : Bool := true
def leaked (attachedMatch : Bool) : Bool := attachedMatch && !catalogFilter
#eval leaked true
