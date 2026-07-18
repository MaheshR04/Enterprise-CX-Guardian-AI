/**
 * Utility to process request query pagination and format responses.
 */
export const getPaginationOptions = (query) => {
  const page = Math.max(1, parseInt(query.page, 10) || 1);
  const limit = Math.max(1, Math.min(100, parseInt(query.limit, 10) || 10)); // caps max limit at 100
  const skip = (page - 1) * limit;

  return { page, limit, skip };
};

export const formatPaginationResponse = (data, totalCount, page, limit) => {
  const totalPages = Math.ceil(totalCount / limit);
  
  return {
    results: data,
    pagination: {
      currentPage: page,
      limit,
      totalResults: totalCount,
      totalPages,
      hasNextPage: page < totalPages,
      hasPrevPage: page > 1
    }
  };
};
