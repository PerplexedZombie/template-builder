{# templates/sproc_template.sql #}
/*

Author: {{ author }}
Created: {{ created_on }}

Error_{{ error_number }} - {{ error_blurb }} ({{ db_ref }}):

Description:    {{ description }}

Commentary:     {{ commentary }}

================================================================================================================
*/


create procedure Error_{{error_number}}
    begin
        /*<Place code here>*/
    end;

