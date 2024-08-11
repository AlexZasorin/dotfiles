-- You can easily change to a different colorscheme.
return {
  -- Change the name of the colorscheme plugin below, and then
  -- change the command in the config to whatever the name of that colorscheme is.
  --
  -- If you want to see what colorschemes are already installed, you can use `:Telescope colorscheme`.
  'AlexZasorin/neosolarized.nvim',
  priority = 1000, -- Make sure to load this before all the other start plugins.
  lazy = false,
  dependencies = {
    'tjdevries/colorbuddy.nvim',
  },
  config = function()
    -- Load the colorscheme here.
    -- Like many other themes, this one has different styles, and you could load
    -- any other, such as 'tokyonight-storm', 'tokyonight-moon', or 'tokyonight-day'.
    require('neosolarized').setup({
      comment_italics = true,
      background_set = true,
    })
    vim.cmd.colorscheme('neosolarized')

    -- You can configure highlights by doing something like:
    vim.cmd.hi('Comment gui=none')
  end,
}
