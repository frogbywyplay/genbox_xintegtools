<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="text"/>
<xsl:template match="target">
  <xsl:for-each select="packages/package[@name = 'busybox']">
    <xsl:if test="public">public</xsl:if>
  </xsl:for-each>
</xsl:template>
</xsl:stylesheet>
