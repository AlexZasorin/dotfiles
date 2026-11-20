return {
  'petertriho/nvim-scrollbar',
  config = function()
    local colors = require('neosolarized').colors
    require('scrollbar').setup({
      scrollbar = {
        thumb = {
          highlight = { bg = colors.base1:to_vim() },
        },
      },
    })
  end,
}
