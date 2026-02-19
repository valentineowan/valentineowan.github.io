/* ===== Footer upgrade: sitemap + logos + note ===== */

.site-footer{
  background: rgba(17,24,39,.02);
}

.footer-top{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:14px;
  flex-wrap:wrap;
  padding-top: 10px;
}

.footer-copy{
  display:flex;
  align-items:center;
  gap:10px;
  flex-wrap:wrap;
  font-size:13px;
  color:var(--muted);
}

.footer-sep{
  opacity:.7;
}

.footer-affil-text{
  color:var(--muted);
}

.footer-note{
  margin-top:10px;
  color:var(--muted);
  font-size:13px;
}

.footer-logos{
  margin-top:14px;
  display:flex;
  align-items:center;
  gap:14px;
  flex-wrap:wrap;
  padding-bottom: 4px;
}

.logo-link{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  padding:8px 10px;
  border-radius:12px;
  border:1px solid var(--line);
  background: rgba(255,255,255,.7);
  text-decoration:none;
}

.logo-link:hover{
  background: rgba(17,24,39,.03);
  border-color: rgba(47,111,237,.25);
}

.footer-logo{
  height:28px;
  width:auto;
  display:block;
  filter: saturate(1.05) contrast(1.03);
}

/* Responsive footer polish */
@media (max-width:720px){
  .footer-top{ gap:10px; }
  .footer-links{ gap:10px; }
  .footer-logo{ height:26px; }
}