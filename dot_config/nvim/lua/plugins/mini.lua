-- Collection of various small independent plugins/modules
return {
  'nvim-mini/mini.nvim',
  config = function()
    -- Better Around/Inside textobjects
    --
    -- Examples:
    --  - va)  - [v]isually select [a]round [)]paren
    --  - yinq - [y]ank [i]nside [n]ext [q]uote
    --  - ci'  - [c]hange [i]nside [']quote
    require('mini.ai').setup({ n_lines = 500 })

    -- Add/delete/replace surroundings (brackets, quotes, etc.)
    --
    -- - saiw) - [s]urround [a]dd [i]nner [w]ord [)]Paren
    -- - sd'   - [s]urround [d]elete [']quotes
    -- - sr)'  - [s]urround [r]eplace [)] [']
    require('mini.surround').setup()

    -- require('mini.pairs').setup()

    -- Move lines/selections with Alt+Shift+hjkl
    require('mini.move').setup({
      mappings = {
        left = '<M-A-h>',
        right = '<M-A-l>',
        down = '<M-A-j>',
        up = '<M-A-k>',
        line_left = '<M-A-h>',
        line_right = '<M-A-l>',
        line_down = '<M-A-j>',
        line_up = '<M-A-k>',
      },
    })

    -- ... and there is more!
    --  Check out: https://github.com/nvim-mini/mini.nvim
  end,
}
