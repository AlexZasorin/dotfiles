return {
  'petertriho/nvim-scrollbar',
  config = function()
    local colors = require('neosolarized').colors
    require('scrollbar').setup({
      handle = {
        color = colors.base1:to_vim(),
      },
    })
  end,
}
