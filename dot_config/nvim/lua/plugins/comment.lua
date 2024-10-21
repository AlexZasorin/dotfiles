--  This is equivalent to:
--    require('Comment').setup({})

-- "gc" to comment visual regions/lines
return { 'numToStr/Comment.nvim', event = { 'BufReadPre', 'BufNewFile' }, opts = {} }
