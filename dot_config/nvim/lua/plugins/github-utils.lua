return {
  'real-erik/github-utils.nvim',
  keys = {
    {
      'gbw',
      function()
        require('github-utils').open_web_client()
      end,
      mode = 'n',
      desc = '[g]it [b]rowse [w]eb',
    },
    {
      'gbf',
      function()
        require('github-utils').open_web_client_file()
      end,
      mode = 'n',
      desc = '[g]it [b]rowse [f]ile',
    },
    {
      'gbl',
      function()
        require('github-utils').create_permalink()
      end,
      mode = 'n',
      desc = '[g]it [b]rowse [l]ink',
    },
  },
}
