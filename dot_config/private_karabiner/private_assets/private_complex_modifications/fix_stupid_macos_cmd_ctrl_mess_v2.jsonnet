local terminal_app_exclusions = [
  '^com\\.apple\\.Terminal$',
  '^com\\.googlecode\\.iterm2$',
  '^com\\.microsoft\\.VSCode$',
  '^com\\.github\\.wez\\.wezterm$',
  // Add any additional applications you wish to exclude
];

local letter_exceptions = ['e'];
local lowercase_letters = [
  if !std.member(letter_exceptions, std.char(i)) then std.char(i) for i in std.range(97, 122) // 'a' to 'z' in ASCII
];

local numbers = [
  std.toString(i) for i in std.range(1, 9)
];

local punctuation = [',', 'slash', '[', ']', '{', ';', '}', '`'];
local all_characters = numbers + lowercase_letters + punctuation;
local bash_shortcut_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'w', 'y', 'z'];

local makeSimpleRule(key_code_from, key_code_to, except_apps=[]) = [
  {
    'type': 'basic',
    'from': {
      'key_code': key_code_from,
      'modifiers': {
        'optional': [],
      },
    },
    'to': [
      {
        'key_code': key_code_to,
      }
    ],
    [if std.length(except_apps) > 0 then 'conditions']: [
      {
        'type': 'frontmost_application_unless',
        'bundle_identifiers': except_apps,
      }
    ],
  },
];

local makeManipulator(from_key, to_key, variable_name) = {
  "type": "basic",
  "conditions": [
    {
      "type": "variable_if",
      "name": variable_name,
      "value": 1
    }
  ],
  "from": {
    "key_code": from_key,
    "modifiers": { "optional": ["any"] }
  },
  "to": [{ "key_code": to_key }]
};

local makeDualRule(mandatory_modifiers, key='', optional_modifiers=[], except_apps=[], pointing_button='') = [
  // Rule to swap Command to Control
  {
    'type': 'basic',
    'from': {
      [if key != '' then 'key_code']: key,
      'modifiers': {
        'mandatory': mandatory_modifiers,
        'optional': optional_modifiers,
      },
      [if pointing_button != '' then 'pointing_button']: pointing_button,
    },
    'to': [{
      [if key != '' then 'key_code']: key,
      'modifiers': [if m == 'command' then 'control' else m for m in mandatory_modifiers],
      [if pointing_button != '' then 'pointing_button']: pointing_button,
    }],
    'conditions': if except_apps != [] then [
      {
        'type': 'frontmost_application_unless',
        'bundle_identifiers': except_apps,
      },
    ] else [],
  },
  // Rule to swap Control to Command
  {
    'type': 'basic',
    'from': {
      [if key != '' then 'key_code']: key,
      'modifiers': {
        'mandatory': [if m == 'command' then 'control' else m for m in mandatory_modifiers],
        'optional': optional_modifiers,
      },
      [if pointing_button != '' then 'pointing_button']: pointing_button,
    },
    'to': [{
      [if key != '' then 'key_code']: key,
      'modifiers': mandatory_modifiers,
      [if pointing_button != '' then 'pointing_button']: pointing_button,
    }],
    'conditions': if except_apps != [] then [
      {
        'type': 'frontmost_application_unless',
        'bundle_identifiers': except_apps,
      },
    ] else [],
  },
];

local commandRules = [
  rules
  for subarray in [
    if std.member(bash_shortcut_letters, i) then makeDualRule(['command'], i, [], terminal_app_exclusions) else makeDualRule(['command'], i) 
    for i in all_characters
  ]
  for rules in subarray
];

local commandShiftRules = [
  rules
  for subarray in [
    if std.member(bash_shortcut_letters, i) then makeDualRule(['command', 'shift'], i, [], terminal_app_exclusions) else makeDualRule(['command', 'shift'], i) 
    for i in all_characters
  ]
  for rules in subarray
];

{
  title: 'Advanced Key Swaps V2',
  rules: [
    {
      description: 'Swap Command and Control for specified shortcuts, with exceptions for certain applications',
      manipulators:
        commandRules +
        makeDualRule(['command'], 'e', [], terminal_app_exclusions + ['^com\\.microsoft\\.Outlook$']) +
        makeDualRule(['command'], '', [], [], 'button1') +
        commandShiftRules +
        makeDualRule(['command', 'option'], 'f') +
        makeSimpleRule('up_arrow', 'vk_none') +
        makeSimpleRule('down_arrow', 'vk_none') +
        makeSimpleRule('left_arrow', 'vk_none') +
        makeSimpleRule('right_arrow', 'vk_none'),
    },
    {
      "description": "Map Caps Lock + hjkl to Arrow Keys with Caps Lock State Tracking",
      "manipulators": [
        makeManipulator("h", "left_arrow", "caps_lock_pressed"),
        makeManipulator("j", "down_arrow", "caps_lock_pressed"),
        makeManipulator("k", "up_arrow", "caps_lock_pressed"),
        makeManipulator("l", "right_arrow", "caps_lock_pressed"),
        {
          "from": {
            "key_code": "caps_lock",
            "modifiers": { "optional": ["any"] }
          },
          "to": [
            { "set_variable": { "name": "caps_lock_pressed", "value": 1 } }
          ],
          "to_after_key_up": [
            { "set_variable": { "name": "caps_lock_pressed", "value": 0 } }
          ],
          "to_if_alone": [{ "key_code": "escape" }],
          "type": "basic"
        }
      ]
    },
  ],
}
