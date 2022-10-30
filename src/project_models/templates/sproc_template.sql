{# templates/sproc_template.sql #}
/*

Author: {{ author }}
Created: {{ created_on }}

Error_{{ error_number }} - {{ error_blurb }} ({{ db_ref }}):

Description:    {{ description }}

Commentary:     {{ commentary }}

================================================================================================================
*/


CREATE Error_{{error_number}} @CVDate DATE
AS
    BEGIN
--         Parameter sniffing OP.
        DECLARE @MonthEnd DATE = COALESCE(@CVDate, CONVERT(varchar,dateadd(d,-(day(getdate())),getdate()),106))

        /*Put Code Here*/
        ;
    END
GO

