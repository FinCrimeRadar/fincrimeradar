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
    },
    3: {
      customerExplanation: {
        intro: [
          'Customer R is contacted.',
          'They sound anxious but cooperate.',
          'They explain that approximately two weeks earlier they responded to an advertisement for remote work.'
        ],
        roleTitle: 'Client Settlement Assistant',
        roleParagraphs: [
          'Customer R says the role involved administrative support and processing payments received from clients.',
          'They were told the company was expanding its UK operation and that new staff would temporarily use personal accounts to process client settlements while additional corporate payment facilities were being established.'
        ]
      },
      provided: [
        'A screenshot of the original job advertisement.',
        'An employment agreement.',
        'A link to a professional looking company website.',
        'WhatsApp communications with someone identifying themselves as an operations manager.',
        'Payment instructions.',
        'A document explaining how staff commission would be calculated.'
      ],
      retainedFundsExplanation: 'Customer R says the £1,220 difference between received and onward funds represented wages, commission and amounts they were instructed to retain pending reconciliation.',
      framingLine: 'At this point these documents establish what Customer R claims happened. They do not establish that the employment was genuine.',
      evidenceItems: [
        { title: 'Customer account of recruitment', status: 'SelfReported' },
        { title: 'Job advertisement screenshot', status: 'SelfReported', note: 'Authenticity not yet established.' },
        { title: 'Employment agreement', status: 'SelfReported', note: 'Authenticity not yet established.' },
        { title: 'Website', status: 'Observed' },
        { title: 'WhatsApp conversation', status: 'SelfReported', note: 'Metadata not yet verified.' },
        { title: 'Payment instruction documents', status: 'SelfReported' },
        { title: 'Claimed commission arrangement', status: 'SelfReported' }
      ],
      hypothesisImpact: {
        A: 'Weakened slightly',
        B: 'Still unresolved',
        C: 'Strengthened',
        D: 'Still uncertain',
        E: 'Weakened if the customer’s explanation is accurate'
      },
      practitionerLens: {
        heading: 'Do not ask whether the documents look professional. Ask whether they can be independently authenticated.',
        body: 'Deceptive employment propositions can include professional looking websites, documentation, interviews and structured onboarding.',
        closing: 'What would you authenticate before deciding whether this employment explanation is genuine?'
      },
      investigationActions: [
        'Verify company registration and trading history.',
        'Verify domain registration history.',
        'Examine message metadata.',
        'Verify recruiter identity.',
        'Compare beneficiary instructions against transaction records.',
        'Check whether the supposed employer has genuine corporate payment infrastructure.',
        'Review whether recruitment materials existed before suspicious activity began.'
      ],
      investigationActionsNote: 'These are reflective prompts only. No selection is scored, recorded or marked correct or incorrect.'
    },
    4: {
      digitalEvidence: {
        paragraphs: [
          'Internal authentication records become available.',
          'All four relevant sessions originated from Customer R’s established mobile device.',
          'The device had been associated with the account for seventeen months.',
          'Normal biometric authentication was used.',
          'There were no password resets immediately before the activity.',
          'There were no newly registered devices.',
          'There was no material change in the normal geographic pattern of account access.',
          'Customer R manually created the new beneficiaries.',
          'Customer R personally confirmed the relevant transfers.',
          'The beneficiary details match instructions contained within the WhatsApp conversation supplied by Customer R.'
        ]
      },
      evidenceItems: [
        { title: 'Established device', status: 'Observed' },
        { title: 'Biometric authentication', status: 'Observed' },
        { title: 'Normal access geography', status: 'Observed' },
        { title: 'Beneficiary creation', status: 'Observed' },
        { title: 'Transfer authorisation', status: 'Observed' },
        { title: 'Beneficiary details matching supplied communications', status: 'Corroborated' }
      ],
      coreMessage: 'Control has become clearer. Intent has not.',
      practitionerLens: {
        heading: 'This evidence answers who performed the account actions. It does not answer why they performed them.',
        body: 'Authentication establishes control much more strongly than intent.'
      },
      gateNote: 'Review all five hypotheses again in light of this evidence before continuing.'
    },
    5: {
      intro: [
        'This compares your initial assessment against your current assessment.',
        'It does not reveal FinCrimeRadar’s own position on the five hypotheses.'
      ]
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
