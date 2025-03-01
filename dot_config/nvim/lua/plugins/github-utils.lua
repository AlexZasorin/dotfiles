return {
  'real-erik/github-utils.nvim',
  keys = {
    {
      'ggw',
      function()
        require('github-utils').open_web_client()
      end,
      mode = 'n',
      desc = '[g]oto [g]ithub [w]eb',
    },
    {
      'ggf',
      function()
        require('github-utils').open_web_client_file()
      end,
      mode = 'n',
      desc = '[g]oto [g]ithub [f]ile',
    },
    {
      'ggp',
      function()
        require('github-utils').create_permalink()
      end,
      mode = 'n',
      desc = '[g]oto [g]ithub line [p]ermalink',
    },
    {
      'gp',
      function()
        require('github-utils').create_permalink()
      end,
      mode = 'v',
      desc = '[g]ithub line range [p]ermalink',
    },
  },
}
