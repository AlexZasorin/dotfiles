return {
  'real-erik/github-utils.nvim',
  keys = {
    {
      'gtw',
      function()
        require('github-utils').open_web_client()
      end,
      mode = 'n',
      desc = '[g]i[t]hub [w]eb',
    },
    {
      'gtf',
      function()
        require('github-utils').open_web_client_file()
      end,
      mode = 'n',
      desc = '[g]i[t]hub [f]ile',
    },
    {
      'gtp',
      function()
        require('github-utils').create_permalink()
      end,
      mode = 'n',
      desc = '[g]i[t]hub line [p]ermalink',
    },
  },
}
