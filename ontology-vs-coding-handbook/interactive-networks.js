(function () {
  var COLORS = {
    object: '#1e40af',
    code: '#b45309',
    frame: '#047857',
    artifact: '#6d28d9',
    theme: '#7c2d12'
  };
  var FILLS = {
    object: '#eff6ff',
    code: '#fffbeb',
    frame: '#ecfdf5',
    artifact: '#f5f3ff',
    theme: '#fff7ed'
  };

  function el(name, attrs) {
    var node = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.keys(attrs || {}).forEach(function (key) {
      node.setAttribute(key, attrs[key]);
    });
    return node;
  }

  function setPressed(buttons, activeButton) {
    buttons.forEach(function (button) {
      var active = button === activeButton;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
  }

  function networkLabels(lang) {
    if (lang === 'ko') {
      return {
        nodes: {
          ontology: '온톨로지\nOntology',
          codingScheme: '코딩 스키마\nCoding scheme',
          framing: '인식론적\n프레이밍',
          student: '학생\nStudent',
          aiTool: 'AI 도구\nAI Tool',
          claim: '주장\nClaim',
          evidence: '증거\nEvidence',
          uncertainty: '불확실성\nUncertainty',
          verification: '검증\nVerification',
          trustHedge: 'AI 신뢰 유보\nAI-trust-hedge',
          outsourcing: '사고 외주화\nOutsourcing',
          confidence: '자신감 회복\nConfidence repair',
          toolDependence: '도구 의존\nTool dependence',
          answer: '답 얻기 프레임\nAnswer-getting',
          sensemaking: '의미 구성 프레임\nSensemaking',
          performance: '수행 프레임\nPerformance'
        },
        notes: {
          all: '<strong>혼합 설명(Hybrid account)</strong>같은 발췌문이 인식론적 대상, 해석 코드, 프레임으로 동시에 읽히지만, 세 층은 서로 다른 근거(warrant)를 가진다.',
          ontology: '<strong>온톨로지 층(Ontology layer)</strong>재사용 가능한 대상(object)과 관계(relation)를 안정화한다: 학생, AI 도구, 주장, 증거, 불확실성, 검증.',
          coding: '<strong>코딩 층(Coding layer)</strong>발화가 이 말뭉치(corpus)에서 하는 해석적 일을 코드(code)로 읽는다.',
          framing: '<strong>프레이밍 층(Framing layer)</strong>학생이 AI 사용을 답 얻기, 의미 구성, 수행 중 어떤 지식 활동으로 지향하는지 본다.',
          hybrid: '<strong>혼합 보기(Hybrid)</strong>온톨로지는 무엇을 안정화할지, 코딩은 발화가 무엇을 하는지, 프레이밍은 지식 활동의 지향을 설명한다.'
        }
      };
    }
    return {
      nodes: {
        ontology: 'Ontology',
        codingScheme: 'Coding\nscheme',
        framing: 'Epistemological\nframing',
        student: 'Student',
        aiTool: 'AI Tool',
        claim: 'Claim',
        evidence: 'Evidence',
        uncertainty: 'Uncertainty',
        verification: 'Verification',
        trustHedge: 'AI-trust-\nhedge',
        outsourcing: 'Outsourcing\nthinking',
        confidence: 'Confidence\nrepair',
        toolDependence: 'Tool\ndependence',
        answer: 'Answer-getting\nframe',
        sensemaking: 'Sensemaking\nframe',
        performance: 'Performance\nframe'
      },
      notes: {
        all: '<strong>Hybrid account</strong>The same excerpt can be read as epistemic objects, interpretive codes, and frames, but each layer has a different warrant.',
        ontology: '<strong>Ontology layer</strong>Stabilizes reusable objects and relations: student, AI tool, claim, evidence, uncertainty, and verification.',
        coding: '<strong>Coding layer</strong>Reads what the utterance is doing in this corpus through interpretive codes.',
        framing: '<strong>Framing layer</strong>Asks whether the student treats AI use as answer-getting, sensemaking, or performance management.',
        hybrid: '<strong>Hybrid view</strong>Ontology names what is stable, coding names what the utterance does, and framing explains orientation to knowledge activity.'
      }
    };
  }

  function initConceptNetwork(widget) {
    var lang = widget.getAttribute('data-lang') || 'en';
    var labels = networkLabels(lang);
    var svg = widget.querySelector('svg');
    var note = widget.querySelector('[data-network-note]');
    var buttons = Array.from(widget.querySelectorAll('[data-network-filter]'));
    var nodes = [
      { id: 'ontology', type: 'artifact', layers: ['ontology', 'hybrid'], x: 120, y: 80 },
      { id: 'codingScheme', type: 'artifact', layers: ['coding', 'hybrid'], x: 380, y: 80 },
      { id: 'framing', type: 'artifact', layers: ['framing', 'hybrid'], x: 620, y: 80 },
      { id: 'student', type: 'object', layers: ['ontology', 'hybrid'], x: 85, y: 210 },
      { id: 'aiTool', type: 'object', layers: ['ontology', 'hybrid'], x: 180, y: 250 },
      { id: 'claim', type: 'object', layers: ['ontology', 'hybrid'], x: 250, y: 170 },
      { id: 'evidence', type: 'object', layers: ['ontology', 'hybrid'], x: 305, y: 285 },
      { id: 'uncertainty', type: 'object', layers: ['ontology', 'hybrid'], x: 165, y: 350 },
      { id: 'verification', type: 'object', layers: ['ontology', 'hybrid'], x: 320, y: 350 },
      { id: 'trustHedge', type: 'code', layers: ['coding', 'hybrid'], x: 390, y: 220 },
      { id: 'outsourcing', type: 'code', layers: ['coding', 'hybrid'], x: 465, y: 325 },
      { id: 'confidence', type: 'code', layers: ['coding', 'hybrid'], x: 520, y: 250 },
      { id: 'toolDependence', type: 'code', layers: ['coding', 'hybrid'], x: 430, y: 390 },
      { id: 'answer', type: 'frame', layers: ['framing', 'hybrid'], x: 620, y: 210 },
      { id: 'sensemaking', type: 'frame', layers: ['framing', 'hybrid'], x: 650, y: 320 },
      { id: 'performance', type: 'frame', layers: ['framing', 'hybrid'], x: 560, y: 380 }
    ];
    nodes.forEach(function (n) {
      n.label = labels.nodes[n.id];
      n.vx = 0;
      n.vy = 0;
    });
    var byId = {};
    nodes.forEach(function (n) { byId[n.id] = n; });
    var links = [
      ['ontology', 'student', 'ontology'], ['ontology', 'aiTool', 'ontology'],
      ['ontology', 'claim', 'ontology'], ['ontology', 'evidence', 'ontology'],
      ['ontology', 'uncertainty', 'ontology'], ['ontology', 'verification', 'ontology'],
      ['codingScheme', 'trustHedge', 'coding'], ['codingScheme', 'outsourcing', 'coding'],
      ['codingScheme', 'confidence', 'coding'], ['codingScheme', 'toolDependence', 'coding'],
      ['trustHedge', 'uncertainty', 'hybrid'], ['trustHedge', 'verification', 'hybrid'],
      ['outsourcing', 'aiTool', 'hybrid'], ['confidence', 'student', 'hybrid'],
      ['framing', 'answer', 'framing'], ['framing', 'sensemaking', 'framing'],
      ['framing', 'performance', 'framing'], ['sensemaking', 'evidence', 'hybrid'],
      ['answer', 'outsourcing', 'hybrid'], ['performance', 'confidence', 'hybrid'],
      ['performance', 'trustHedge', 'hybrid']
    ].map(function (d) {
      return { source: byId[d[0]], target: byId[d[1]], layer: d[2] };
    });

    var linkGroup = el('g');
    var nodeGroup = el('g');
    svg.appendChild(linkGroup);
    svg.appendChild(nodeGroup);

    links.forEach(function (link) {
      link.el = el('line', { class: 'network-link' });
      link.el.addEventListener('mouseenter', function () {
        note.innerHTML = labels.notes[link.layer] || labels.notes.all;
      });
      linkGroup.appendChild(link.el);
    });

    nodes.forEach(function (node) {
      var g = el('g', { class: 'network-node' });
      var circle = el('circle', { r: node.type === 'artifact' ? 28 : 22, fill: FILLS[node.type], stroke: COLORS[node.type], 'stroke-width': 2 });
      var text = el('text', { class: 'node-label', 'text-anchor': 'middle' });
      node.label.split('\n').forEach(function (line, i, arr) {
        var tspan = el('tspan', { x: 0, dy: i ? 13 : (arr.length > 1 ? -4 : 4) });
        tspan.textContent = line;
        text.appendChild(tspan);
      });
      g.appendChild(circle);
      g.appendChild(text);
      g.addEventListener('mouseenter', function () {
        note.innerHTML = '<strong>' + node.label.replace(/\n/g, ' ') + '</strong>' + (labels.notes[node.layers[0]] || labels.notes.all);
      });
      g.addEventListener('pointerdown', function (event) {
        node.dragging = true;
        g.setPointerCapture(event.pointerId);
      });
      g.addEventListener('pointermove', function (event) {
        if (!node.dragging) return;
        var rect = svg.getBoundingClientRect();
        node.x = (event.clientX - rect.left) * 760 / rect.width;
        node.y = (event.clientY - rect.top) * 440 / rect.height;
        node.vx = 0;
        node.vy = 0;
        draw();
      });
      g.addEventListener('pointerup', function (event) {
        node.dragging = false;
        g.releasePointerCapture(event.pointerId);
      });
      node.el = g;
      nodeGroup.appendChild(g);
    });

    var activeFilter = 'all';
    function visible(d) {
      return activeFilter === 'all' || d.layers.indexOf(activeFilter) !== -1 || d.layer === activeFilter;
    }
    function draw() {
      links.forEach(function (link) {
        link.el.setAttribute('x1', link.source.x);
        link.el.setAttribute('y1', link.source.y);
        link.el.setAttribute('x2', link.target.x);
        link.el.setAttribute('y2', link.target.y);
        link.el.classList.toggle('dim', !visible(link));
      });
      nodes.forEach(function (node) {
        node.x = Math.max(32, Math.min(728, node.x));
        node.y = Math.max(34, Math.min(406, node.y));
        node.el.setAttribute('transform', 'translate(' + node.x + ',' + node.y + ')');
        node.el.classList.toggle('dim', activeFilter !== 'all' && node.layers.indexOf(activeFilter) === -1);
      });
    }
    function tick() {
      links.forEach(function (link) {
        var dx = link.target.x - link.source.x;
        var dy = link.target.y - link.source.y;
        var dist = Math.sqrt(dx * dx + dy * dy) || 1;
        var desired = link.layer === 'hybrid' ? 105 : 88;
        var force = (dist - desired) * 0.004;
        var fx = dx / dist * force;
        var fy = dy / dist * force;
        if (!link.source.dragging) { link.source.vx += fx; link.source.vy += fy; }
        if (!link.target.dragging) { link.target.vx -= fx; link.target.vy -= fy; }
      });
      for (var i = 0; i < nodes.length; i++) {
        for (var j = i + 1; j < nodes.length; j++) {
          var a = nodes[i], b = nodes[j];
          var dx = b.x - a.x;
          var dy = b.y - a.y;
          var dist2 = dx * dx + dy * dy || 1;
          var repulse = 110 / dist2;
          if (!a.dragging) { a.vx -= dx * repulse; a.vy -= dy * repulse; }
          if (!b.dragging) { b.vx += dx * repulse; b.vy += dy * repulse; }
        }
      }
      nodes.forEach(function (node) {
        if (node.dragging) return;
        node.vx += (380 - node.x) * 0.0008;
        node.vy += (235 - node.y) * 0.0008;
        node.vx *= 0.86;
        node.vy *= 0.86;
        node.x += node.vx;
        node.y += node.vy;
      });
      draw();
      requestAnimationFrame(tick);
    }
    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        activeFilter = button.getAttribute('data-network-filter');
        setPressed(buttons, button);
        note.innerHTML = labels.notes[activeFilter] || labels.notes.all;
        draw();
      });
    });
    draw();
    requestAnimationFrame(tick);
  }

  function sortingText(lang) {
    if (lang === 'ko') {
      return {
        zones: [
          { id: 'class', label: '온톨로지 클래스\nOntology class', x: 24, y: 24, w: 340, h: 160 },
          { id: 'code', label: '해석 코드\nInterpretive code', x: 396, y: 24, w: 340, h: 160 },
          { id: 'theme', label: '주제\nTheme', x: 24, y: 230, w: 340, h: 160 },
          { id: 'frame', label: '프레임\nFrame', x: 396, y: 230, w: 340, h: 160 }
        ],
        cards: [
          { label: 'Claim', best: 'class', feedback: '주장(claim)은 연구를 넘어 재사용 가능한 인식론적 대상(epistemic object)이므로 ontology class로 잘 작동한다.' },
          { label: 'AI-trust-hedge', best: 'code', feedback: 'AI 신뢰 유보(AI-trust-hedge)는 이 corpus에서 발화가 하는 해석적 일을 가리키므로 interpretive code에 가깝다.' },
          { label: 'Responsible AI use', best: 'theme', feedback: '책임 있는 AI 사용은 여러 code를 묶어 더 큰 의미 패턴을 설명하므로 theme에 가깝다.' },
          { label: 'Sensemaking', best: 'frame', feedback: '의미 구성(sensemaking)은 참여자가 지금 어떤 knowledge activity가 일어난다고 보는지 설명하므로 frame이다.' },
          { label: 'Evidence source', best: 'class', feedback: '증거 출처(evidence source)는 여러 연구에서 안정적으로 재사용할 수 있는 object다.' },
          { label: 'Confidence repair', best: 'code', feedback: '자신감 회복(confidence repair)은 특정 발화가 수행하는 identity work를 해석하는 code다.' }
        ],
        correct: '맞음',
        close: '다시 생각'
      };
    }
    return {
      zones: [
        { id: 'class', label: 'Ontology class', x: 24, y: 24, w: 340, h: 160 },
        { id: 'code', label: 'Interpretive code', x: 396, y: 24, w: 340, h: 160 },
        { id: 'theme', label: 'Theme', x: 24, y: 230, w: 340, h: 160 },
        { id: 'frame', label: 'Frame', x: 396, y: 230, w: 340, h: 160 }
      ],
      cards: [
        { label: 'Claim', best: 'class', feedback: 'Claim works as an ontology class because it can be reused across studies as an epistemic object.' },
        { label: 'AI-trust-hedge', best: 'code', feedback: 'AI-trust-hedge is better as an interpretive code because it names what an utterance is doing in this corpus.' },
        { label: 'Responsible AI use', best: 'theme', feedback: 'Responsible AI use is broader than one segment; it can organize several codes into a theme.' },
        { label: 'Sensemaking', best: 'frame', feedback: 'Sensemaking is a frame because it describes what kind of knowledge activity the participant treats as happening.' },
        { label: 'Evidence source', best: 'class', feedback: 'Evidence source is a reusable object that can travel across studies and tools.' },
        { label: 'Confidence repair', best: 'code', feedback: 'Confidence repair reads the identity work performed by a particular utterance.' }
      ],
      correct: 'Good fit',
      close: 'Reconsider'
    };
  }

  function initSortingMap(widget) {
    var lang = widget.getAttribute('data-lang') || 'en';
    var data = sortingText(lang);
    var svg = widget.querySelector('svg');
    var note = widget.querySelector('[data-sort-note]');
    var zoneGroup = el('g');
    var cardGroup = el('g');
    svg.appendChild(zoneGroup);
    svg.appendChild(cardGroup);
    data.zones.forEach(function (zone) {
      var g = el('g');
      var rect = el('rect', { class: 'sort-zone', x: zone.x, y: zone.y, width: zone.w, height: zone.h, rx: 8 });
      var text = el('text', { class: 'zone-label', x: zone.x + 14, y: zone.y + 24 });
      zone.label.split('\n').forEach(function (line, i) {
        var tspan = el('tspan', { x: zone.x + 14, dy: i ? 14 : 0 });
        tspan.textContent = line;
        text.appendChild(tspan);
      });
      zone.rect = rect;
      g.appendChild(rect);
      g.appendChild(text);
      zoneGroup.appendChild(g);
    });
    data.cards.forEach(function (card, index) {
      card.x = 292 + (index % 2) * 150;
      card.y = 178 + Math.floor(index / 2) * 42;
      var g = el('g', { class: 'sort-card' });
      var rect = el('rect', { width: 136, height: 32, rx: 16, fill: '#ffffff', stroke: COLORS[card.best === 'class' ? 'object' : card.best], 'stroke-width': 1.5 });
      var text = el('text', { class: 'sort-label', x: 68, y: 21, 'text-anchor': 'middle' });
      text.textContent = card.label;
      g.appendChild(rect);
      g.appendChild(text);
      function drawCard() {
        g.setAttribute('transform', 'translate(' + card.x + ',' + card.y + ')');
      }
      g.addEventListener('pointerdown', function (event) {
        card.dragging = true;
        card.dx = event.offsetX - card.x;
        card.dy = event.offsetY - card.y;
        g.setPointerCapture(event.pointerId);
      });
      g.addEventListener('pointermove', function (event) {
        if (!card.dragging) return;
        var rectBox = svg.getBoundingClientRect();
        card.x = (event.clientX - rectBox.left) * 760 / rectBox.width - 68;
        card.y = (event.clientY - rectBox.top) * 440 / rectBox.height - 16;
        card.x = Math.max(4, Math.min(620, card.x));
        card.y = Math.max(4, Math.min(396, card.y));
        data.zones.forEach(function (zone) {
          var cx = card.x + 68, cy = card.y + 16;
          zone.rect.classList.toggle('active', cx >= zone.x && cx <= zone.x + zone.w && cy >= zone.y && cy <= zone.y + zone.h);
        });
        drawCard();
      });
      g.addEventListener('pointerup', function (event) {
        card.dragging = false;
        g.releasePointerCapture(event.pointerId);
        data.zones.forEach(function (zone) { zone.rect.classList.remove('active'); });
        var cx = card.x + 68, cy = card.y + 16;
        var zone = data.zones.find(function (z) { return cx >= z.x && cx <= z.x + z.w && cy >= z.y && cy <= z.y + z.h; });
        if (zone) {
          note.innerHTML = '<strong>' + (zone.id === card.best ? data.correct : data.close) + ': ' + card.label + '</strong>' + card.feedback;
        }
      });
      drawCard();
      cardGroup.appendChild(g);
    });
  }

  document.querySelectorAll('[data-widget="concept-network"]').forEach(initConceptNetwork);
  document.querySelectorAll('[data-widget="sorting-map"]').forEach(initSortingMap);
})();
