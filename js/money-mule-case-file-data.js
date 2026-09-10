window.MMC_DATA = {
  stages: {
    2: {
      alert: {
        heading: 'The Alert',
        paragraphs: [
          'At 16:52 on Thursday, the fraud operations queue generates a high priority receiving account alert.',
          'Customer R has received £11,420 from four previously unseen individuals in four days.',
          '£10,200 has already moved onwards.',
          'Three new beneficiaries have been used.',
          'One transaction involved a cash withdrawal.',
          'The payment pattern is materially different from Customer R’s established account behaviour.',
          'A sending institution has separately notified the firm that one of the inbound payments originated from an authorised push payment fraud victim.',
          'The transactions require investigation.',
          'They do not yet establish Customer R’s intent.'
        ]
      },
      profile: {
        heading: 'Customer profile',
        fields: [
          { label: 'Customer', value: 'Customer R' },
          { label: 'Age', value: '24' },
          { label: 'Account tenure', value: '3 years and 2 months' },
          { label: 'Primary account use', value: 'Salary, rent, groceries, card spending and ordinary transfers' },
          { label: 'Previous average monthly credits', value: 'Approximately £1,730' },
          { label: 'Employment position', value: 'Temporary employment ended seven weeks ago' },
          { label: 'Recent income', value: 'Materially reduced' },
          { label: 'Previous comparable payment behaviour', value: 'None identified' },
          { label: 'Previous confirmed fraud', value: 'None identified' },
          { label: 'Previous National Fraud Database record', value: 'None identified' },
          { label: 'Recorded vulnerability', value: 'None currently recorded' }
        ],
        vulnerabilityCallout: 'The absence of a previously recorded vulnerability is not evidence that no vulnerability exists.'
      },
      chronology: [
        {
          day: 1,
          incoming: { sender: 'Sender A', amount: 2850 },
          outgoing: { type: 'transfer', beneficiary: 'new beneficiary', amount: 2500 },
          timeToMoveLabel: 'Time to onward movement',
          timeToMove: '26 minutes'
        },
        {
          day: 2,
          incoming: { sender: 'Sender B', amount: 3200 },
          outgoing: { type: 'transfer', beneficiary: 'new beneficiary', amount: 3000 },
          timeToMoveLabel: 'Time to onward movement',
          timeToMove: '19 minutes'
        },
        {
          day: 3,
          incoming: { sender: 'Sender C', amount: 1760 },
          outgoing: { type: 'withdrawal', beneficiary: null, amount: 1500 },
          timeToMoveLabel: 'Time to withdrawal',
          timeToMove: '36 minutes'
        },
        {
          day: 4,
          incoming: { sender: 'Sender D', amount: 3610 },
          outgoing: { type: 'transfer', beneficiary: 'new beneficiary', amount: 3200 },
          timeToMoveLabel: 'Time to onward movement',
          timeToMove: '16 minutes'
        }
      ],
      totals: { received: 11420, moved: 10200, difference: 1220 },
      suggestedHypotheses: { A: 'Plausible', B: 'Unresolved', C: 'Plausible', D: 'Unresolved', E: 'Plausible' },
      gateNote: 'The practitioner must review all five hypotheses before continuing.',
      practitionerLensIntro: 'What can you actually establish at this stage?',
      practitionerLensCanEstablish: [
        'You can establish that unusual funds entered the account.',
        'You can establish that most were moved rapidly.',
        'You can establish that the behaviour materially differs from the customer’s historical activity.',
        'You can establish that at least one sending institution has reported fraud.'
      ],
      practitionerLensCannotEstablish: [
        'You cannot yet establish who controlled the transactions.',
        'You cannot establish what Customer R believed.',
        'You cannot establish why Customer R moved the funds.',
        'You cannot establish whether Customer R received a benefit knowingly.',
        'You cannot establish whether somebody else influenced or controlled the activity.'
      ],
      practitionerLensClosing: 'Do not let the transaction pattern answer a customer intent question that has not yet been investigated.'
    }
  },
  hypotheses: {
    A: {
      name: 'Knowing Participation',
      description: 'The customer understood the illicit nature of the arrangement and deliberately facilitated the movement of funds.'
    },
    B: {
      name: 'Participation After Emerging Suspicion',
      description: 'The customer may not have understood the arrangement initially, but evidence later indicates growing suspicion followed by continued participation. This is an investigative hypothesis, not a declaration of criminal liability.'
    },
    C: {
      name: 'Deceived Participation',
      description: 'The customer genuinely believed the activity had a legitimate explanation such as employment, commerce, investment or helping another person.'
    },
    D: {
      name: 'Financial Exploitation or Coercion',
      description: 'The customer was manipulated, controlled, threatened, groomed or otherwise exploited.'
    },
    E: {
      name: 'Account Compromise',
      description: 'The account holder did not authorise or meaningfully participate in the relevant activity.'
    }
  },
  sources: {}
};
