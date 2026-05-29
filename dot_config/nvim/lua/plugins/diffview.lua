return {
  'sindrets/diffview.nvim',
  dependencies = {
    'nvim-lua/plenary.nvim',
    'nvim-tree/nvim-web-devicons',
  },
  cmd = {
    'DiffviewOpen',
    'DiffviewClose',
    'DiffviewFileHistory',
    'DiffviewToggleFiles',
    'DiffviewFocusFiles',
    'DiffviewRefresh',
  },
  keys = {
    { '<leader>df', '<cmd>DiffviewFileHistory %<CR>', desc = '[d]iffview [f]ile history' },
    { '<leader>df', ":'<,'>DiffviewFileHistory<CR>", mode = 'v', desc = '[d]iffview [f]ile history (range)' },
    { '<leader>dr', '<cmd>DiffviewFileHistory<CR>', desc = '[d]iffview [r]epo history' },
    { '<leader>do', '<cmd>DiffviewOpen<CR>', desc = '[d]iffview [o]pen' },
    { '<leader>dc', '<cmd>DiffviewClose<CR>', desc = '[d]iffview [c]lose' },
    { '<leader>dt', '<cmd>DiffviewToggleFiles<CR>', desc = '[d]iffview [t]oggle files' },
    { '<leader>dF', '<cmd>DiffviewFocusFiles<CR>', desc = '[d]iffview [F]ocus files' },
    { '<leader>dR', '<cmd>DiffviewRefresh<CR>', desc = '[d]iffview [R]efresh' },
  },
  opts = {
    keymaps = {
      view = {
        { 'n', 'q', '<cmd>DiffviewClose<CR>', { desc = 'Close Diffview' } },
      },
      file_panel = {
        { 'n', 'q', '<cmd>DiffviewClose<CR>', { desc = 'Close Diffview' } },
      },
      file_history_panel = {
        { 'n', 'q', '<cmd>DiffviewClose<CR>', { desc = 'Close Diffview' } },
      },
      option_panel = {
        { 'n', 'q', '<cmd>DiffviewClose<CR>', { desc = 'Close Diffview' } },
      },
    },
  },
}
