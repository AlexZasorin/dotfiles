return {
  'jvgrootveld/telescope-zoxide',
  dependencies = { 'nvim-telescope/telescope.nvim' },
  keys = {
    { '<leader>wp', '<cmd>Telescope zoxide list<CR>', desc = 'Switch project (zoxide)' },
  },
  config = function()
    require('telescope').load_extension('zoxide')
  end,
}
