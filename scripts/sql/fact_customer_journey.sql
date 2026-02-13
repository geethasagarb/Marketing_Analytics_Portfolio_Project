-- Common Table Expression (CTE) to identify and tag duplicate records
WITH DuplicateRecords AS (
	SELECT
		JourneyID,
		CustomerID,
		ProductID,
		VisitDate,
		Stage,
		Action,
		Duration,
		-- Use ROW_NUMBER() to assign a unique row number to each record within the partition defined below
		ROW_NUMBER() OVER (
		-- PARTITION BY groups the rows based on the specified columns that should be unique
			PARTITION BY CustomerID, ProductID, VisitDate, Stage, Action
			ORDER BY JourneyID
		) AS row_num
	FROM 
		dbo.customer_journey
)
-- Select all records from the CTE where row_num > 1, which indicates duplicate entries
SELECT *
FROM DuplicateRecords
WHERE row_num > 1
ORDER BY JourneyID;


-- Outer Query selects the final cleaned and standardized data
SELECT 
	JourneyID,
	CustomerID,
	ProductID,
	VisitDate,
	Stage,
	Action,
	COALESCE(Duration, avg_duration) AS Duration -- replaces missing duration with the average durations for the corresponding
FROM
	(
		-- Subquery to process and clean the data
		SELECT 
			JourneyID,
			CustomerID,
			ProductID,
			VisitDate,
			UPPER(Stage) AS Stage,
			Action,
			Duration,
			AVG(Duration) OVER (PARTITION BY VisitDate) AS avg_duration,
			ROW_NUMBER() OVER (
				PARTITION BY CustomerID, ProductID, VisitDate, UPPER(Stage),Action
				ORDER BY JourneyID
			) AS row_num -- assigning a row number to each row within the partition to identify duplicates
		 FROM 
			dbo.customer_journey
		) AS subquery
	WHERE 
		row_num = 1;