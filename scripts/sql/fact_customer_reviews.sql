-- Query to Clean whitespaces in the ReviewText Column

SELECT
	ReviewID,
	CustomerID,
	ProductID,
	ReviewDate,
	Rating,
	REPLACE(ReviewText, '  ', ' ') AS ReviewText
FROM dbo.customer_reviews;
	