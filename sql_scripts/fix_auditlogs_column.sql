USE School_Management_198;
GO

-- First, let's check the actual structure of the AuditLogs_198 table
PRINT 'Current structure of AuditLogs_198 table:';
SELECT 
    c.name AS ColumnName,
    t.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable
FROM 
    sys.columns c
JOIN 
    sys.types t ON c.user_type_id = t.user_type_id
WHERE 
    c.object_id = OBJECT_ID('AuditLogs_198')
ORDER BY 
    c.column_id;

-- There are two possibilities:
-- 1. The column doesn't exist and needs to be added
-- 2. The column exists but with a different name (like 'UserName' instead of 'Username')

-- First check if there's a similarly named column that might be the right one
DECLARE @potential_username_column VARCHAR(100);
SELECT @potential_username_column = c.name
FROM sys.columns c
WHERE c.object_id = OBJECT_ID('AuditLogs_198') 
AND c.name LIKE '%user%'
AND c.name != 'Username';

IF @potential_username_column IS NOT NULL
BEGIN
    PRINT 'Found potential username column: ' + @potential_username_column;
    PRINT 'You may need to update your application code to use this column name instead.';
END
ELSE
BEGIN
    -- If no similar column exists, add the Username column
    IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('AuditLogs_198') AND name = 'Username')
    BEGIN
        PRINT 'Adding Username column to AuditLogs_198 table...';
        ALTER TABLE AuditLogs_198 
        ADD Username NVARCHAR(50) NULL;
        PRINT 'Username column added successfully.';
    END
    ELSE
    BEGIN
        PRINT 'Username column already exists in the table.';
    END
END

-- Print the updated structure
PRINT 'Updated structure of AuditLogs_198 table:';
SELECT 
    c.name AS ColumnName,
    t.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable
FROM 
    sys.columns c
JOIN 
    sys.types t ON c.user_type_id = t.user_type_id
WHERE 
    c.object_id = OBJECT_ID('AuditLogs_198')
ORDER BY 
    c.column_id;
