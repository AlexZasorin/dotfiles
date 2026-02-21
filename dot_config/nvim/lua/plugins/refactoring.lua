-- refactoring.nvim
-- https://github.com/ThePrimeagen/refactoring.nvim

return {
  'ThePrimeagen/refactoring.nvim',
  dependencies = {
    'nvim-lua/plenary.nvim',
    'nvim-treesitter/nvim-treesitter',
  },
  keys = {
    {
      '<leader>re',
      ':Refactor extract ',
      mode = 'x',
      desc = '[r]efactor [e]xtract function',
    },
    {
      '<leader>rX',
      ':Refactor extract_to_file ',
      mode = 'x',
      desc = '[r]efactor e[X]tract function to file',
    },
    {
      '<leader>rv',
      ':Refactor extract_var ',
      mode = 'x',
      desc = '[r]efactor extract [v]ariable',
    },
    {
      '<leader>ri',
      ':Refactor inline_var',
      mode = { 'n', 'x' },
      desc = '[r]efactor [i]nline variable',
    },
    {
      '<leader>rI',
      ':Refactor inline_func',
      mode = 'n',
      desc = '[r]efactor [I]nline function',
    },
    {
      '<leader>rb',
      ':Refactor extract_block',
      mode = 'n',
      desc = '[r]efactor extract [b]lock',
    },
    {
      '<leader>rB',
      ':Refactor extract_block_to_file',
      mode = 'n',
      desc = '[r]efactor extract [B]lock to file',
    },
  },
  opts = {},
}
