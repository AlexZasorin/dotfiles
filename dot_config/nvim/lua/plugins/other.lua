return {
  'rgroli/other.nvim',
  keys = {
    { 'go', '<cmd>Other<CR>', desc = 'Open other file' },
    { 'gso', '<cmd>OtherVSplit<CR>', desc = 'Open other file in vertical split' },
  },
  dependencies = { 'nvim-lua/plenary.nvim' },
  config = function()
    require('other-nvim').setup({
      mappings = {
        -- builtin mappings
        -- 'react',
        -- custom mapping
        {
          pattern = '/(.*)/(.*).ts$',
          target = '/%1/%2.spec.ts',
        },
        {
          pattern = '/(.*)/(.*).tsx$',
          target = '/%1/%2.spec.tsx',
        },
        {
          pattern = '/(.*)/(.*).js$',
          target = '/%1/%2.spec.js',
        },
        {
          pattern = '/(.*)/(.*).jsx$',
          target = '/%1/%2.spec.jsx',
        },
        {
          pattern = '/(.*)/(.*).spec.ts$',
          target = '/%1/%2.ts',
        },
        {
          pattern = '/(.*)/(.*).spec.tsx$',
          target = '/%1/%2.tsx',
        },
        {
          pattern = '/(.*)/(.*).spec.js$',
          target = '/%1/%2.js',
        },
        {
          pattern = '/(.*)/(.*).spec.jsx$',
          target = '/%1/%2.jsx',
        },
      },
      -- transformers = {
      --   -- defining a custom transformer
      --   lowercase = function(inputString)
      --     return inputString:lower()
      --   end,
      -- },
      -- keybindings = {
      --   go = 'open_file()',
      --   gs = 'open_file_vs()',
      -- },
      style = {
        -- How the plugin paints its window borders
        -- Allowed values are none, single, double, rounded, solid and shadow
        border = 'solid',

        -- Column seperator for the window
        seperator = '|',

        -- width of the window in percent. e.g. 0.5 is 50%, 1.0 is 100%
        width = 0.7,

        -- min height in rows.
        -- when more columns are needed this value is extended automatically
        minHeight = 2,
      },
    })
  end,
}
