
/*

Author: Terry Dullaghan
Created: 2022-09-20

Error_1515 - Data is invalid. (SpecialDB):

Description:    This is what happens when you let monkeys use type writers...

Commentary:     Have you tried not hiring monkeys?

================================================================================================================
*/


CREATE Error_1515 @CVDate DATE
AS
    BEGIN
--         Parameter sniffing OP.
        DECLARE @MonthEnd DATE = COALESCE(@CVDate, CONVERT(varchar,dateadd(d,-(day(getdate())),getdate()),106))

        /*Put Code Here*/
        ;
    END
GO
