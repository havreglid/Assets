## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005

# Thanks to Requies and Elhoim from CivFanatics for this interface mod

from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import math
import IconGrid
############################################
### BEGIN CHANGES ENHANCED INTERFACE MOD ###
############################################
import IconGrid_BUG
#from IconGrid_BUG import IconGrid_BUG
##########################################
### END CHANGES ENHANCED INTERFACE MOD ###
##########################################

import CvForeignAdvisor
import DomPyHelpers
import TechTree
import AttitudeUtil
import BugCore
import BugDll
import BugUtil
import DealUtil
import DiplomacyUtil
import FavoriteCivicDetector
import FontUtil
import TradeUtil
import re

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

PyPlayer = DomPyHelpers.DomPyPlayer
PyCity = DomPyHelpers.DomPyCity

AdvisorOpt = BugCore.game.Advisors

# tech trade columns
(iTechColLeader,
 iTechColStatus,
 iTechColWants,
 iTechColCantYou,
 iTechColResearch,
 iTechColGold,
 iTechColWill,
 iTechColWont,
 iTechColCantThem,
) = range(9)

# Debugging help
def ExoticForPrint (stuff):
	stuff = "ExoForAdv: " + stuff
	BugUtil.debug(stuff)

# this class is shared by both the resource and technology foreign advisors
class CvExoticForeignAdvisor (CvForeignAdvisor.CvForeignAdvisor):
	"Exotic Foreign Advisor Screen"

	def __init__(self):
		CvForeignAdvisor.CvForeignAdvisor.__init__ (self)
		self.iScreen = -1
		self.nWidgetCount = 0
		self.nLineCount = 0
		self.WIDGET_ID = "ForeignAdvisorWidget"
		self.LINE_ID = "ForeignAdvisorLine"
		self.SCREEN_NAME = "ForeignAdvisor"
		self.DEBUG_DROPDOWN_ID =  "ForeignAdvisorDropdownWidget"
		self.EXIT_ID = "ForeignAdvisorExitWidget"
		self.BACKGROUND_ID = "ForeignAdvisorBackground"
		self.W_SCREEN = 1024
		self.H_SCREEN = 768
		self.Y_TITLE = 8
		self.X_LEADER = 80
		self.Y_LEADER = 115
		self.W_LEADER = 64

		self.SCREEN_DICT = {
			"BONUS": 0,
			"TECH": 1,
			"RELATIONS": 2,
			"ACTIVE_TRADE": 3,
			"INFO": 4,
			"GLANCE": 5,
			}

		self.X_EXIT = self.W_SCREEN - 10
		self.Y_EXIT = self.H_SCREEN - 42
		self.X_LINK = 0
		self.Y_LINK = self.H_SCREEN - 42
		self.DX_LINK = (self.X_EXIT - self.X_LINK) / (len (self.SCREEN_DICT) + 1)
		self.Y_BOTTOM_PANEL = self.H_SCREEN - 55

		self.X_LEGEND = 20
		self.Y_LEGEND = 530
		self.H_LEGEND = 180
		self.W_LEGEND = 160
		self.MARGIN_LEGEND = 10
		
		self.X_LEADER_CIRCLE_TOP = self.W_SCREEN /2
		self.Y_LEADER_CIRCLE_TOP = 87
		
		self.RADIUS_LEADER_ARC = 480
		self.LINE_WIDTH = 6
		
		self.iSelectedLeader = -1
		self.iActiveLeader = -1
		self.listSelectedLeaders = []
		self.iShiftKeyDown = 0

#		help (CyPlayer)
#		help (CyGInterfaceScreen)
		self.GLANCE_HEADER = "ForeignAdvisorGlanceHeader"
		self.GLANCE_BUTTON = "ForeignAdvisorPlusMinus"
		self.X_LINK = 0
		self.Y_LINK = 726
		
		self.X_GLANCE_OFFSET = 10
		self.Y_GLANCE_OFFSET = 3
		self.GLANCE_BUTTON_SIZE = 46
		self.PLUS_MINUS_SIZE = 25
		self.bGlancePlus = True

		self.INFO_BORDER = 10
## Surplus Type Start ##
		self.iSurplus = -1
## Surplus Type End ##
## Relations Start ##
		self.bContactLine = False
		self.bWarLine = False
		self.bDefensiveLine = False
		self.bOpenBorderLine = False
		self.bTeamLine = False
		self.bVassalLine = False
		self.bHideVassal = False
		self.bHideTeam = False
## Relations End ##

############################################
### BEGIN CHANGES ENHANCED INTERFACE MOD ###
############################################

		###################
		# General options #
		###################
		
		# Show the names of the leaders if 'True'
		self.SHOW_LEADER_NAMES = False
		
		# Show a border around the rows
		self.SHOW_ROW_BORDERS = True
		
		# Minimum space at the top and bottom of the screen.
		self.MIN_TOP_BOTTOM_SPACE = 60
		
		# Minimum space at the left and right end of the screen.
		self.MIN_LEFT_RIGHT_SPACE = 25
		
		# Extra border at the left and right ends of the column groups (import/export)
		self.GROUP_BORDER = 8
		
		# Extra space before the label of the column groups (import/export)
		self.GROUP_LABEL_OFFSET = "   "
		
		# Minimum space between the columns
		self.MIN_COLUMN_SPACE = 5
		
		# Minimum space between the rows
		self.MIN_ROW_SPACE = 1
		
		##########################
		# Resources view options #
		##########################
		
		# If 'True', the amount for each surplus resource is subtracted by one. So it shows how many you
		# can give away without losing the resource yourself. This value isn't affected by any default 
		# layout.
		self.RES_SHOW_EXTRA_AMOUNT = True
		
		# If 'True', the amount's are shown as an overlay on top of the lower left corner of the resources.
		# If 'False', the amount's are shown below the resources so you'll need to use a higher value for 
		# self.RES_SURPLUS_HEIGHT (see below).
		self.RES_SHOW_SURPLUS_AMOUNT_ON_TOP = True
		
		# If 'True', the resource columns are grouped as import and export.
		self.RES_SHOW_IMPORT_EXPORT_HEADER = True
		
		# If 'True', two extra columns are used to display resources that are traded in active deals.
		self.RES_SHOW_ACTIVE_TRADE = True
		
		# Height of the panel showing the surplus resources. If self.RES_SHOW_SURPLUS_AMOUNT_ON_TOP is 'False'
		# you'll need to set a higher value for this variable (110 is recommended).
## Platy Bonus Screen ##
		self.RES_SURPLUS_HEIGHT = 4 * 24 + 50
## Platy Bonus Screen ##
		
		self.RES_GOLD_COL_WIDTH = 25
		
		# Space between the two panels.
		self.RES_PANEL_SPACE = 0
		
		#############################
		# Technologies view options #
		#############################
		
		# If 'True', use icon size 32x32
		# If 'False', use icon size 64x64
		self.TECH_USE_SMALL_ICONS = True
		
		self.TECH_STATUS_COL_WIDTH = 40
		self.TECH_GOLD_COL_WIDTH = 60
		
		###############
		# End options #
		###############
		
		self.TITLE_HEIGHT = 24
		self.TABLE_CONTROL_HEIGHT = 24
		self.RESOURCE_ICON_SIZE = 34
		self.SCROLL_TABLE_UP = 1
		self.SCROLL_TABLE_DOWN = 2

##########################################
### END CHANGES ENHANCED INTERFACE MOD ###
##########################################
		
		self.SCREEN_DICT = {
			"BONUS": 0,
			"TECH": 1,
			"RELATIONS": 2,
			"ACTIVE_TRADE": 3,
			"INFO": 4,
			"GLANCE": 5,
			}

		self.REV_SCREEN_DICT = {}

		for key, value in self.SCREEN_DICT.items():
			self.REV_SCREEN_DICT[value] = key

		self.DRAW_DICT = {
			"BONUS": self.drawResourceDeals,
			"TECH": self.drawTechDeals,
			"RELATIONS": self.drawRelations,
			"ACTIVE_TRADE": self.drawActive,
			"INFO": self.drawInfo,
			"GLANCE": self.drawGlance,
			}

		self.TXT_KEY_DICT = {
			"BONUS": "TXT_KEY_FOREIGN_ADVISOR_RESOURCES",
			"TECH": "TXT_KEY_FOREIGN_ADVISOR_TECHS",
			"RELATIONS": "TXT_KEY_FOREIGN_ADVISOR_RELATIONS",
			"ACTIVE_TRADE": "TXT_KEY_FOREIGN_ADVISOR_ACTIVE",
			"INFO": "TXT_KEY_FOREIGN_ADVISOR_INFO",
			"GLANCE": "TXT_KEY_FOREIGN_ADVISOR_GLANCE",
			}

		self.ORDER_LIST = ["RELATIONS", \
											 "GLANCE", \
											 "ACTIVE_TRADE", \
											 "BONUS", \
											 "INFO", \
											 "TECH"]

		self.iDefaultScreen = self.SCREEN_DICT["RELATIONS"]
						
	def interfaceScreen (self, iScreen):
	
		self.ATTITUDE_DICT = {
			"COLOR_GREEN": re.sub (":", "|", CyTranslator().getText ("TXT_KEY_ATTITUDE_FRIENDLY", ())),
			"COLOR_CYAN" : re.sub (":", "|", CyTranslator().getText ("TXT_KEY_ATTITUDE_PLEASED", ())),
			"COLOR_MAGENTA" : re.sub (":", "|", CyTranslator().getText ("TXT_KEY_ATTITUDE_ANNOYED", ())),
			"COLOR_RED" : re.sub (":", "|", CyTranslator().getText ("TXT_KEY_ATTITUDE_FURIOUS", ())),
			}

		self.WAR_ICON = smallSymbol(FontSymbols.WAR_CHAR)
		self.PEACE_ICON = smallSymbol(FontSymbols.PEACE_CHAR)

		self.objTechTree = TechTree.TechTree()

		if (iScreen < 0):
			iScreen = self.iScreen
			if (self.iScreen < 0):
				iScreen = self.iDefaultScreen
			else:
				iScreen = self.iScreen
		
		self.EXIT_TEXT = u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + u"</font>"
		self.SCREEN_TITLE = u"<font=4b>" + localText.getText("TXT_KEY_FOREIGN_ADVISOR_TITLE", ()).upper() + u"</font>"

		if (self.iScreen != iScreen):	
			self.killScreen()
			self.iScreen = iScreen
		
		screen = self.getScreen()
		if screen.isActive():
			return
		screen.setRenderInterfaceOnly(True);
		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		self.iActiveLeader = CyGame().getActivePlayer()
		self.iSelectedLeader = self.iActiveLeader
		self.listSelectedLeaders = []
		#self.listSelectedLeaders.append(self.iSelectedLeader)

############################################
### BEGIN CHANGES ENHANCED INTERFACE MOD ###
############################################
		#self.W_SCREEN = screen.getXResolution()
		#self.H_SCREEN = screen.getYResolution()

		# RJG Start - following line added as per RJG (http://forums.civfanatics.com/showpost.php?p=6996936&postcount=15)
		# FROM BUG MA Widescreen START
		# over-ride screen width, height
		self.W_SCREEN = screen.getXResolution() - 40
		self.X_SCREEN = (screen.getXResolution() - 24) / 2
		self.L_SCREEN = 20

		if self.W_SCREEN < 1024:
			self.W_SCREEN = 1024
			self.L_SCREEN = 0
		
		self.X_EXIT = self.W_SCREEN - 30
		# FROM BUG MA Widescreen END
		
		#self.X_EXIT = self.W_SCREEN - 10
		# RJG End
		self.DX_LINK = (self.X_EXIT - self.X_LINK) / (len (self.SCREEN_DICT) + 1)

		self.Y_EXIT = self.H_SCREEN - 42
		self.Y_LINK = self.H_SCREEN - 42
		self.Y_BOTTOM_PANEL = self.H_SCREEN - 55
		
		# Set the background and exit button, and show the screen
		screen.setDimensions(0, 0, self.W_SCREEN, self.H_SCREEN)
		screen.addDrawControl(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addPanel( "TopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
		screen.addPanel( "BottomPanel", u"", u"", True, False, 0, self.Y_BOTTOM_PANEL, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )
##########################################
### END CHANGES ENHANCED INTERFACE MOD ###
##########################################

		# Set the background and exit button, and show the screen
		# RJG Start - following line added as per RJG (http://forums.civfanatics.com/showpost.php?p=6996936&postcount=15)
#		screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)
		screen.setDimensions(self.L_SCREEN, screen.centerY(0), self.W_SCREEN, self.H_SCREEN)
		# RJG end
		screen.showWindowBackground(False)
		screen.setText(self.EXIT_ID, "", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		self.nWidgetCount = 0
		self.nLineCount = 0
		
		if (CyGame().isDebugMode()):
			self.szDropdownName = self.getWidgetName(self.DEBUG_DROPDOWN_ID)
			screen.addDropDownBoxGFC(self.szDropdownName, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
			for j in range(gc.getMAX_PLAYERS()):
				if (gc.getPlayer(j).isAlive()):
					bSelected = False
					if j == self.iActiveLeader:
						bSelected = True
					screen.addPullDownString(self.szDropdownName, gc.getPlayer(j).getName(), j, j, bSelected )

		CyInterface().setDirty(InterfaceDirtyBits.Foreign_Screen_DIRTY_BIT, False)
		
		# Draw leader heads
		self.drawContents(True)
				
	# Drawing Leaderheads
	def drawContents(self, bInitial):
	
		if (self.iScreen < 0):
			return
						
		self.objActiveLeader = gc.getPlayer(self.iActiveLeader)
		self.iActiveTeam = self.objActiveLeader.getTeam()
		self.objActiveTeam = gc.getTeam(self.iActiveTeam)
		self.deleteAllWidgets()
		
		screen = self.getScreen()

		# Header...
		screen.setLabel(self.getNextWidgetName(), "", self.SCREEN_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.W_SCREEN / 2, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
	
		if (self.REV_SCREEN_DICT.has_key(self.iScreen)):
			self.DRAW_DICT[self.REV_SCREEN_DICT[self.iScreen]] (bInitial)
		else:
			return
## Platy Foreign Start ##
		# Link to other Foreign advisor screens
		xLink = self.DX_LINK / 2;
		self.drawLinks()
## Platy Foreign End ##
		for i in range (len (self.ORDER_LIST)):
			szScreen = self.ORDER_LIST[i]
# BUG - Glance Tab - start
			if szScreen == "GLANCE" and not AdvisorOpt.isShowGlance():
				continue # skip the GLANCE label
# BUG - Glance Tab - end
			szTextId = self.getNextWidgetName()
			if (self.iScreen != self.SCREEN_DICT[szScreen]):
				screen.setText (szTextId, "", u"<font=4>" + localText.getText (self.TXT_KEY_DICT[szScreen], ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, xLink, self.Y_LINK, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_FOREIGN_ADVISOR, self.SCREEN_DICT[szScreen], -1)
			else:
				screen.setText (szTextId, "", u"<font=4>" + localText.getColorText (self.TXT_KEY_DICT[szScreen], (), gc.getInfoTypeForString ("COLOR_YELLOW")).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, xLink, self.Y_LINK, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_FOREIGN_ADVISOR, -1, -1)
			xLink += self.DX_LINK
	def drawRelations(self, bInitial):
		screen = self.getScreen()
		if self.iShiftKeyDown == 1:
			if (self.iSelectedLeader in self.listSelectedLeaders):
				self.listSelectedLeaders.remove(self.iSelectedLeader)
			else:
				self.listSelectedLeaders.append(self.iSelectedLeader)
		else:
			self.listSelectedLeaders = []
			if (not bInitial):
				self.listSelectedLeaders.append(self.iSelectedLeader)	

		bNoLeadersSelected = (len(self.listSelectedLeaders) == 0)
		bSingleLeaderSelected = (len(self.listSelectedLeaders) == 1)
		if bSingleLeaderSelected:
			self.iSelectedLeader = self.listSelectedLeaders[0]

		# legend
		iButtonSize = 16
		ButtonArt = CyArtFileMgr().getInterfaceArtInfo("WORLDBUILDER_TOGGLE_UNIT_EDIT_MODE").getPath()
		ButtonBorder = CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_RED_X").getPath()

		x = self.X_LEGEND + self.MARGIN_LEGEND
		y = self.Y_LEGEND + self.MARGIN_LEGEND
		screen.setLabel(self.getNextWidgetName(), "", u"<font=2>" + CyTranslator().getText("TXT_KEY_FOREIGN_ADVISOR_CONTACT", ()) + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, x, y-10, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		sLineName = self.getNextWidgetName()
		screen.addCheckBoxGFC(sLineName, ButtonArt, ButtonBorder, x - 15, y - 10, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, 1801, -1, ButtonStyles.BUTTON_STYLE_IMAGE)
		screen.setState(sLineName, self.bContactLine)

		y += 3 * self.MARGIN_LEGEND
		screen.setLabel(self.getNextWidgetName(), "", u"<font=2>" + CyTranslator().getText("TXT_KEY_CONCEPT_WAR", ()) + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, x, y-10, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		sLineName = self.getNextWidgetName()
		screen.addCheckBoxGFC(sLineName, ButtonArt, ButtonBorder, x - 15, y - 10, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, 1802, -1, ButtonStyles.BUTTON_STYLE_IMAGE)
		screen.setState(sLineName, self.bWarLine)

		y += 3 * self.MARGIN_LEGEND
		screen.setLabel(self.getNextWidgetName(), "", u"<font=2>" + CyTranslator().getText("TXT_KEY_TRADE_DEFENSIVE_PACT_STRING", ()) + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, x, y-10, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		sLineName = self.getNextWidgetName()
		screen.addCheckBoxGFC(sLineName, ButtonArt, ButtonBorder, x - 15, y - 10, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, 1803, -1, ButtonStyles.BUTTON_STYLE_IMAGE)
		screen.setState(sLineName, self.bDefensiveLine)

		y += 3 * self.MARGIN_LEGEND
		screen.setLabel(self.getNextWidgetName(), "", u"<font=2>" + CyTranslator().getText("TXT_KEY_TRADE_OPEN_BORDERS_STRING", ()) + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, x, y-10, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		sLineName = self.getNextWidgetName()
		screen.addCheckBoxGFC(sLineName, ButtonArt, ButtonBorder, x - 15, y - 10, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, 1804, -1, ButtonStyles.BUTTON_STYLE_IMAGE)
		screen.setState(sLineName, self.bOpenBorderLine)

		y += 3 * self.MARGIN_LEGEND
		screen.setLabel(self.getNextWidgetName(), "", u"<font=2>" + CyTranslator().getText("TXT_KEY_PITBOSS_TEAM", ()) + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, x, y-10, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		sLineName = self.getNextWidgetName()
		screen.addCheckBoxGFC(sLineName, ButtonArt, ButtonBorder, x - 15, y - 10, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, 1805, -1, ButtonStyles.BUTTON_STYLE_IMAGE)
		screen.setState(sLineName, self.bTeamLine)

		y += 3 * self.MARGIN_LEGEND
		screen.setLabel(self.getNextWidgetName(), "", u"<font=2>" + CyTranslator().getText("TXT_KEY_MISC_VASSAL_SHORT", ()) + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, x, y-10, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		sLineName = self.getNextWidgetName()
		screen.addCheckBoxGFC(sLineName, ButtonArt, ButtonBorder, x - 15, y - 10, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, 1806, -1, ButtonStyles.BUTTON_STYLE_IMAGE)
		screen.setState(sLineName, self.bVassalLine)

		x = self.X_LEGEND + self.MARGIN_LEGEND
		y = self.Y_TITLE + 50
		screen.setLabel(self.getNextWidgetName(), "", u"<font=2>" + CyTranslator().getText("TXT_KEY_HIDE_VASSALS", ()) + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, x, y, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		sLineName = self.getNextWidgetName()
		screen.addCheckBoxGFC(sLineName, ButtonArt, ButtonBorder, x - 15, y, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, 1807, -1, ButtonStyles.BUTTON_STYLE_IMAGE)
		screen.setState(sLineName, self.bHideVassal)

		y += 2 * self.MARGIN_LEGEND
		screen.setLabel(self.getNextWidgetName(), "", u"<font=2>" + CyTranslator().getText("TXT_KEY_HIDE_TEAM", ()) + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, x, y, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		sLineName = self.getNextWidgetName()
		screen.addCheckBoxGFC(sLineName, ButtonArt, ButtonBorder, x - 15, y, iButtonSize, iButtonSize, WidgetTypes.WIDGET_GENERAL, 1808, -1, ButtonStyles.BUTTON_STYLE_IMAGE)
		screen.setState(sLineName, self.bHideTeam)

		iCount = 0
		leaderMap = { }
		for iPlayer in xrange(gc.getMAX_CIV_PLAYERS()):
			player = gc.getPlayer(iPlayer)
			if (player.isAlive() and iPlayer != self.iActiveLeader and (gc.getTeam(player.getTeam()).isHasMet(gc.getPlayer(self.iActiveLeader).getTeam()) or gc.getGame().isDebugMode())):
				if self.bHideVassal and gc.getTeam(player.getTeam()).isAVassal(): continue
				if self.bHideTeam and gc.getTeam(player.getTeam()).getLeaderID() != iPlayer: continue
				leaderMap[iPlayer] = iCount
				iCount += 1
		fLeaderTop = self.Y_LEADER_CIRCLE_TOP
		fRadius = self.RADIUS_LEADER_ARC - self.W_LEADER
		fLeaderArcTop = fLeaderTop + self.W_LEADER + 10
		
		iLeaderWidth = self.W_LEADER
		if iCount < 8:
			iLeaderWidth = int(3 * self.W_LEADER / 2)
	
		# angle increment in radians (180 degree range)
		if (iCount < 2):
			deltaTheta = 0
		else:
			deltaTheta = 3.1415927 / (iCount - 1)

		playerActive = gc.getPlayer(self.iActiveLeader)
		szLeaderHead = self.getNextWidgetName()
		screen.addCheckBoxGFC(szLeaderHead, gc.getLeaderHeadInfo(playerActive.getLeaderType()).getButton(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_LEADER_CIRCLE_TOP - iLeaderWidth/2, int(fLeaderTop), iLeaderWidth, iLeaderWidth, WidgetTypes.WIDGET_LEADERHEAD, self.iActiveLeader, -1, ButtonStyles.BUTTON_STYLE_LABEL)
		screen.setState(szLeaderHead, self.iActiveLeader in self.listSelectedLeaders)
		szName = self.getNextWidgetName()
		sColor = u"<color=%d,%d,%d,%d>" %(playerActive.getPlayerTextColorR(), playerActive.getPlayerTextColorG(), playerActive.getPlayerTextColorB(), playerActive.getPlayerTextColorA())
		szLeaderName = u"<font=3>" + sColor + playerActive.getName() + u"</color></font>"
		screen.setLabel(szName, "", szLeaderName, CvUtil.FONT_CENTER_JUSTIFY, self.X_LEADER_CIRCLE_TOP, fLeaderTop + iLeaderWidth, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		for iPlayer in leaderMap.keys():
			player = gc.getPlayer(iPlayer)

			if bSingleLeaderSelected:
				# attitudes shown are towards single selected leader
				iBaseLeader = self.iSelectedLeader
			else:
				# attitudes shown are towards active leader
				iBaseLeader = self.iActiveLeader
			playerBase = gc.getPlayer(iBaseLeader)

			fX = int(self.X_LEADER_CIRCLE_TOP - fRadius * math.cos(deltaTheta * leaderMap[iPlayer]) - iLeaderWidth/2) 
			fY = int(fLeaderArcTop + fRadius * math.sin(deltaTheta * leaderMap[iPlayer]) - iLeaderWidth/2)

			szLeaderHead = self.getNextWidgetName()
			screen.addCheckBoxGFC(szLeaderHead, gc.getLeaderHeadInfo(player.getLeaderType()).getButton(), CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), int(fX), int(fY), iLeaderWidth, iLeaderWidth, WidgetTypes.WIDGET_LEADERHEAD, iPlayer, iBaseLeader, ButtonStyles.BUTTON_STYLE_LABEL)
			screen.setState(szLeaderHead, iPlayer in self.listSelectedLeaders)
				
			szName = self.getNextWidgetName()
			sColor = u"<color=%d,%d,%d,%d>" %(player.getPlayerTextColorR(), player.getPlayerTextColorG(), player.getPlayerTextColorB(), player.getPlayerTextColorA())
			szText = u"<font=3>" + sColor + player.getName() + u"</color></font>"
			if (gc.getTeam(player.getTeam()).isVassal(playerBase.getTeam())):
				szText = CyTranslator().getText("[ICON_SILVER_STAR]", ()) + szText
			elif (gc.getTeam(playerBase.getTeam()).isVassal(player.getTeam())):
				szText = CyTranslator().getText("[ICON_STAR]", ()) + szText
			screen.setLabel(szName, "", szText, CvUtil.FONT_CENTER_JUSTIFY, fX + iLeaderWidth/2, fY + iLeaderWidth, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

			# Leader attitude towards active player
			szName = self.getNextWidgetName()
			lVincent = ["INTERFACE_ATTITUDE_0", "INTERFACE_ATTITUDE_1", "INTERFACE_ATTITUDE_2", "INTERFACE_ATTITUDE_3", "INTERFACE_ATTITUDE_4"]
			
			if (gc.getTeam(player.getTeam()).isHasMet(playerBase.getTeam()) and iBaseLeader != iPlayer):
				sButton = lVincent[gc.getPlayer(iPlayer).AI_getAttitude(iBaseLeader)]
				iButtonWidth = iLeaderWidth/3
				screen.setImageButton(szName, CyArtFileMgr().getInterfaceArtInfo(sButton).getPath(), int(fX), int(fY) + iLeaderWidth - iButtonWidth, iButtonWidth, iButtonWidth, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		
		x = self.X_LEGEND + self.MARGIN_LEGEND
		y = self.Y_LEGEND + 2 * self.MARGIN_LEGEND
		screen.addLineGFC(self.BACKGROUND_ID, self.getNextLineName(), x, y, x + self.W_LEGEND - 2*self.MARGIN_LEGEND, y, gc.getInfoTypeForString("COLOR_WHITE"))
		y += 3 * self.MARGIN_LEGEND
		screen.addLineGFC(self.BACKGROUND_ID, self.getNextLineName(), x, y, x + self.W_LEGEND - 2*self.MARGIN_LEGEND, y, gc.getInfoTypeForString("COLOR_RED"))
		y += 3 * self.MARGIN_LEGEND
		screen.addLineGFC(self.BACKGROUND_ID, self.getNextLineName(), x, y, x + self.W_LEGEND - 2*self.MARGIN_LEGEND, y, gc.getInfoTypeForString("COLOR_BLUE"))
		y += 3 * self.MARGIN_LEGEND
		screen.addLineGFC(self.BACKGROUND_ID, self.getNextLineName(), x, y, x + self.W_LEGEND - 2*self.MARGIN_LEGEND, y, gc.getInfoTypeForString("COLOR_CITY_GREEN"))
		y += 3 * self.MARGIN_LEGEND
		screen.addLineGFC(self.BACKGROUND_ID, self.getNextLineName(), x, y, x + self.W_LEGEND - 2*self.MARGIN_LEGEND, y, gc.getInfoTypeForString("COLOR_YELLOW"))
		y += 3 * self.MARGIN_LEGEND
		screen.addLineGFC(self.BACKGROUND_ID, self.getNextLineName(), x, y, x + self.W_LEGEND - 2*self.MARGIN_LEGEND, y, gc.getInfoTypeForString("COLOR_CYAN"))

		for iSelectedLeader in xrange(gc.getMAX_CIV_PLAYERS()):
			bDisplayed = (gc.getPlayer(iSelectedLeader).isAlive() and (gc.getGame().isDebugMode() or gc.getTeam(gc.getPlayer(self.iActiveLeader).getTeam()).isHasMet(gc.getPlayer(iSelectedLeader).getTeam())))
			if self.bHideVassal and gc.getTeam(gc.getPlayer(iSelectedLeader).getTeam()).isAVassal(): continue
			if self.bHideTeam and gc.getTeam(gc.getPlayer(iSelectedLeader).getTeam()).getLeaderID() != iSelectedLeader: continue
			if iSelectedLeader in self.listSelectedLeaders or (bNoLeadersSelected and bDisplayed):
				# get selected player and location
				if (iSelectedLeader in leaderMap):
					thetaSelected = deltaTheta * leaderMap[iSelectedLeader]
					fXSelected = self.X_LEADER_CIRCLE_TOP - fRadius * math.cos(thetaSelected)
					fYSelected = fLeaderArcTop + fRadius * math.sin(thetaSelected)
				else:
					fXSelected = self.X_LEADER_CIRCLE_TOP
					fYSelected = fLeaderTop + iLeaderWidth/2
				
				for iPlayer in leaderMap.keys():
					player = gc.getPlayer(iPlayer)

					fX = self.X_LEADER_CIRCLE_TOP - fRadius * math.cos(deltaTheta * leaderMap[iPlayer])
					fY = fLeaderArcTop + fRadius * math.sin(deltaTheta * leaderMap[iPlayer])

					# draw lines
					if (iSelectedLeader != iPlayer):
						if (player.getTeam() == gc.getPlayer(iSelectedLeader).getTeam()):
							if not self.bTeamLine:
								szName = self.getNextLineName()
								screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), int(fX), int(fY), gc.getInfoTypeForString("COLOR_YELLOW") )						
						elif (gc.getTeam(player.getTeam()).isVassal(gc.getPlayer(iSelectedLeader).getTeam()) or gc.getTeam(gc.getPlayer(iSelectedLeader).getTeam()).isVassal(player.getTeam())):
							if not self.bVassalLine:
								szName = self.getNextLineName()
								screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), int(fX), int(fY), gc.getInfoTypeForString("COLOR_CYAN") )						
						elif (gc.getTeam(player.getTeam()).isHasMet(gc.getPlayer(iSelectedLeader).getTeam())):
							if (gc.getTeam(player.getTeam()).isAtWar(gc.getPlayer(iSelectedLeader).getTeam())):
								if not self.bWarLine:
									szName = self.getNextLineName()
									screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), int(fX), int(fY), gc.getInfoTypeForString("COLOR_RED") )
							else:
								bJustPeace = True
								if (gc.getTeam(player.getTeam()).isOpenBorders(gc.getPlayer(iSelectedLeader).getTeam())):
									if not self.bOpenBorderLine:
										fDy = fYSelected - fY
										fDx = fXSelected - fX
										fTheta = math.atan2(fDy, fDx)
										if (fTheta > 0.5 * math.pi):
											fTheta -= math.pi
										elif (fTheta < -0.5 * math.pi):
											fTheta += math.pi
										fSecondLineOffsetY = self.LINE_WIDTH * math.cos(fTheta)
										fSecondLineOffsetX = -self.LINE_WIDTH * math.sin(fTheta)
										szName = self.getNextLineName()
										screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected + fSecondLineOffsetX), int(fYSelected + fSecondLineOffsetY), int(fX + fSecondLineOffsetX), int(fY + fSecondLineOffsetY), gc.getInfoTypeForString("COLOR_CITY_GREEN") )
									bJustPeace = False
								if (gc.getTeam(player.getTeam()).isDefensivePact(gc.getPlayer(iSelectedLeader).getTeam())):
									if not self.bDefensiveLine:
										szName = self.getNextLineName()
										screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), int(fX), int(fY), gc.getInfoTypeForString("COLOR_BLUE") )
									bJustPeace = False
								if (bJustPeace):
									if not self.bContactLine:
										szName = self.getNextLineName()
										screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), int(fX), int(fY), gc.getInfoTypeForString("COLOR_WHITE") )

				player = gc.getPlayer(self.iActiveLeader)
				if (player.getTeam() == gc.getPlayer(iSelectedLeader).getTeam()):
					if not self.bTeamLine:
						szName = self.getNextLineName()
						screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), self.X_LEADER_CIRCLE_TOP, fLeaderTop + iLeaderWidth/2, gc.getInfoTypeForString("COLOR_YELLOW") )
				elif (gc.getTeam(player.getTeam()).isVassal(gc.getPlayer(iSelectedLeader).getTeam()) or gc.getTeam(gc.getPlayer(iSelectedLeader).getTeam()).isVassal(player.getTeam())):
					if not self.bVassalLine:
						szName = self.getNextLineName()
						screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), self.X_LEADER_CIRCLE_TOP, fLeaderTop + iLeaderWidth/2, gc.getInfoTypeForString("COLOR_CYAN") )
				elif (gc.getTeam(player.getTeam()).isHasMet(gc.getPlayer(iSelectedLeader).getTeam())):
					if (gc.getTeam(player.getTeam()).isAtWar(gc.getPlayer(iSelectedLeader).getTeam())):
						if not self.bWarLine:
							szName = self.getNextLineName()
							screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), self.X_LEADER_CIRCLE_TOP, fLeaderTop + iLeaderWidth/2, gc.getInfoTypeForString("COLOR_RED") )
					else:
						bJustPeace = True
						if (gc.getTeam(player.getTeam()).isOpenBorders(gc.getPlayer(iSelectedLeader).getTeam())):
							if not self.bOpenBorderLine:
								fDy = fLeaderTop + iLeaderWidth/2 - fYSelected
								fDx = self.X_LEADER_CIRCLE_TOP - fXSelected
								fTheta = math.atan2(fDy, fDx)
								if (fTheta > 0.5 * math.pi):
									fTheta -= math.pi
								elif (fTheta < -0.5 * math.pi):
									fTheta += math.pi
								fSecondLineOffsetY = self.LINE_WIDTH * math.cos(fTheta)
								fSecondLineOffsetX = -self.LINE_WIDTH * math.sin(fTheta)
								szName = self.getNextLineName()
								screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected + fSecondLineOffsetX), int(fYSelected + fSecondLineOffsetY), int(self.X_LEADER_CIRCLE_TOP + fSecondLineOffsetX), int(fLeaderTop + iLeaderWidth/2 + fSecondLineOffsetY), gc.getInfoTypeForString("COLOR_CITY_GREEN") )
							bJustPeace = False
						if (gc.getTeam(player.getTeam()).isDefensivePact(gc.getPlayer(iSelectedLeader).getTeam())):
							if not self.bDefensiveLine:
								szName = self.getNextLineName()
								screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), int(self.X_LEADER_CIRCLE_TOP), int(fLeaderTop + iLeaderWidth/2), gc.getInfoTypeForString("COLOR_BLUE") )
							bJustPeace = False
						if (bJustPeace):
							if not self.bContactLine:
								szName = self.getNextLineName()
								screen.addLineGFC(self.BACKGROUND_ID, szName, int(fXSelected), int(fYSelected), int(self.X_LEADER_CIRCLE_TOP), int(fLeaderTop + iLeaderWidth/2), gc.getInfoTypeForString("COLOR_WHITE") )
	
	def drawActive (self, bInitial):
		screen = self.getScreen()

		# Get the Players
		playerActive = gc.getPlayer(self.iActiveLeader)
					
		# Put everything inside a main panel, so we get vertical scrolling
		mainPanelName = self.getNextWidgetName()
		screen.addPanel(mainPanelName, "", "", True, True, 50, 100, self.W_SCREEN - 100, self.H_SCREEN - 200, PanelStyles.PANEL_STYLE_EMPTY)

		# loop through all players and sort them by number of active deals
		listPlayers = [(0,0)] * gc.getMAX_PLAYERS()
		nNumPLayers = 0
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			if (gc.getPlayer(iLoopPlayer).isAlive() and iLoopPlayer != self.iActiveLeader and not gc.getPlayer(iLoopPlayer).isBarbarian() and  not gc.getPlayer(iLoopPlayer).isMinorCiv()):
				if (gc.getTeam(gc.getPlayer(iLoopPlayer).getTeam()).isHasMet(gc.getPlayer(self.iActiveLeader).getTeam()) or gc.getGame().isDebugMode()):
					nDeals = 0				
					for i in range(gc.getGame().getIndexAfterLastDeal()):
						deal = gc.getGame().getDeal(i)
						if ((deal.getFirstPlayer() == iLoopPlayer and deal.getSecondPlayer() == self.iActiveLeader) or (deal.getSecondPlayer() == iLoopPlayer and deal.getFirstPlayer() == self.iActiveLeader)):
							nDeals += 1
					listPlayers[nNumPLayers] = (nDeals, iLoopPlayer)
					nNumPLayers += 1
		listPlayers.sort()
		listPlayers.reverse()

		# loop through all players and display leaderheads
		for j in range (nNumPLayers):
			iLoopPlayer = listPlayers[j][1]

			# Player panel
			playerPanelName = self.getNextWidgetName()
			screen.attachPanel(mainPanelName, playerPanelName, gc.getPlayer(iLoopPlayer).getName(), "", False, True, PanelStyles.PANEL_STYLE_MAIN)

			screen.attachLabel(playerPanelName, "", "   ")

			screen.attachImageButton(playerPanelName, "", gc.getLeaderHeadInfo(gc.getPlayer(iLoopPlayer).getLeaderType()).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, -1, False)
						
			innerPanelName = self.getNextWidgetName()
			screen.attachPanel(playerPanelName, innerPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)

			dealPanelName = self.getNextWidgetName()
			screen.attachListBoxGFC(innerPanelName, dealPanelName, "", TableStyles.TABLE_STYLE_EMPTY)	
			screen.enableSelect(dealPanelName, False)

			iRow = 0
			for i in range(gc.getGame().getIndexAfterLastDeal()):
				deal = gc.getGame().getDeal(i)

				if (deal.getFirstPlayer() == iLoopPlayer and deal.getSecondPlayer() == self.iActiveLeader and not deal.isNone()) or (deal.getSecondPlayer() == iLoopPlayer and deal.getFirstPlayer() == self.iActiveLeader):
					szDealText = CyGameTextMgr().getDealString(deal, iLoopPlayer)
					if AdvisorOpt.isShowDealTurnsLeft():
						if BugDll.isPresent():
							if not deal.isCancelable(self.iActiveLeader, False):
								if deal.isCancelable(self.iActiveLeader, True):
									szDealText += u" %s" % BugUtil.getText("INTERFACE_CITY_TURNS", (deal.turnsToCancel(self.iActiveLeader),))
								else:
									# don't bother adding "This deal cannot be canceled" message
									#szDealText += u" (%s)" % deal.getCannotCancelReason(self.iActiveLeader)
									pass
						else:
							iTurns = DealUtil.Deal(deal).turnsToCancel(self.iActiveLeader)
							if iTurns > 0:
								szDealText += u" %s" % BugUtil.getText("INTERFACE_CITY_TURNS", (iTurns,))
					screen.appendListBoxString(dealPanelName, szDealText, WidgetTypes.WIDGET_DEAL_KILL, deal.getID(), -1, CvUtil.FONT_LEFT_JUSTIFY)
					iRow += 1

#	RJG Start
	def drawRelations (self, bInitial):
		screen = self.getScreen()
		self.W_SCREEN = screen.getXResolution() - 40
		self.X_SCREEN = (screen.getXResolution() - 24) / 2
		self.X_LEADER_CIRCLE_TOP = self.X_SCREEN
		CvForeignAdvisor.CvForeignAdvisor.drawRelations (self, bInitial)
#	RJG End

	def drawInfo (self, bInitial):
		if AdvisorOpt.isUseImprovedEFAInfo():
			self.drawInfoImproved(bInitial)
		else:
			self.drawInfoOriginal(bInitial)

	def drawInfoOriginal (self, bInitial):
#		ExoticForPrint ("Entered drawInfo")

		screen = self.getScreen()

		# Get the Players
		playerActive = gc.getPlayer(self.iActiveLeader)
					
		# Put everything inside a main panel, so we get vertical scrolling
		mainPanelName = self.getNextWidgetName()
		screen.addPanel(mainPanelName, "", "", True, True, 50, 100, self.W_SCREEN - 100, self.H_SCREEN - 200, PanelStyles.PANEL_STYLE_EMPTY)

		ltCivicOptions = range (gc.getNumCivicOptionInfos())

		# loop through all players and display leaderheads
		for iLoopPlayer in xrange(gc.getMAX_CIV_PLAYERS()):
			pLoopPlayer = gc.getPlayer(iLoopPlayer)
			if (pLoopPlayer.isAlive() and iLoopPlayer != self.iActiveLeader and (gc.getTeam(pLoopPlayer.getTeam()).isHasMet(gc.getPlayer(self.iActiveLeader).getTeam()) or CyGame().isDebugMode()) and not pLoopPlayer.isMinorCiv()):
## Platy Info Screen ##
				screen.appendTableRow("InfoTable")
				nPlayerReligion = pLoopPlayer.getStateReligion()
				ReligionInfo = gc.getReligionInfo (nPlayerReligion)
				iLeader = pLoopPlayer.getLeaderType()
				LeaderInfo = gc.getLeaderHeadInfo(iLeader)
				iCivilization = pLoopPlayer.getCivilizationType()
				CivilizationInfo = gc.getCivilizationInfo(iCivilization)
				sColor = u"<color=%d,%d,%d,%d>" %(pLoopPlayer.getPlayerTextColorR(), pLoopPlayer.getPlayerTextColorG(), pLoopPlayer.getPlayerTextColorB(), pLoopPlayer.getPlayerTextColorA())

				sText = "<font=3>" + sColor + pLoopPlayer.getName() + " ["
				bFirst = True
				for i in xrange(gc.getNumTraitInfos()):
					if pLoopPlayer.hasTrait(i):
						if bFirst:
							bFirst = False
						else:
							sText += "/"
						sText += CyTranslator().getText(gc.getTraitInfo(i).getShortDescription(), ())
				sText += "]</color></font>"
				screen.setTableText("InfoTable", 0, iRow, sText, LeaderInfo.getButton(), WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, -1, CvUtil.FONT_LEFT_JUSTIFY )
				screen.setTableText("InfoTable", 1, iRow, "<font=3>" + sColor + pLoopPlayer.getCivilizationShortDescription(0) + "</color></font>", CivilizationInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCivilization, 1, CvUtil.FONT_LEFT_JUSTIFY )
				screen.setTableInt("InfoTable", 2, iRow, "<font=3>" + str(self.calculateTrade (self.iActiveLeader, iLoopPlayer)) + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY )
				if nPlayerReligion > -1:
					if pLoopPlayer.hasHolyCity(nPlayerReligion):
						sText = u"<font=4>%c</font>" %(ReligionInfo.getHolyCityChar())
					else:
						sText = u"<font=4>%c</font>" %(ReligionInfo.getChar())
					screen.setTableText("InfoTable", 3, iRow, sText, "", WidgetTypes.WIDGET_HELP_RELIGION, nPlayerReligion, 1, CvUtil.FONT_CENTER_JUSTIFY )
				iColumn = 4
				if not CyGame().isOption(GameOptionTypes.GAMEOPTION_RANDOM_PERSONALITIES):
					nFavoriteReligion = LeaderInfo.getFavoriteReligion()
					if nFavoriteReligion > -1:
						objReligionInfo = gc.getReligionInfo (nFavoriteReligion)
						screen.setTableText("InfoTable", iColumn, iRow, "", objReligionInfo.getButton(), WidgetTypes.WIDGET_HELP_RELIGION, nFavoriteReligion, 1, CvUtil.FONT_CENTER_JUSTIFY )
					iColumn += 1
				for i in xrange(gc.getNumCivicOptionInfos()):
					nCivic = pLoopPlayer.getCivics (i)
					screen.setTableText("InfoTable", i + iColumn, iRow, "", gc.getCivicInfo (nCivic).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nCivic, 1, CvUtil.FONT_LEFT_JUSTIFY )

				# Don't show favorite civic if playing with Random Personalities.
				if not CyGame().isOption(GameOptionTypes.GAMEOPTION_RANDOM_PERSONALITIES):
					nFavoriteCivic = LeaderInfo.getFavoriteCivic()
					if nFavoriteCivic > -1:
						objCivicInfo = gc.getCivicInfo (nFavoriteCivic)
						screen.setTableText("InfoTable", i + iColumn + 1, iRow, "<font=3>" + objCivicInfo.getDescription() + "</font>", objCivicInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nFavoriteCivic, 1, CvUtil.FONT_LEFT_JUSTIFY )
				iRow += 1
## Platy Info Screen ##

	def drawInfoImproved (self, bInitial):
		screen = self.getScreen()

		# Some spacing variables to help with the layout
		iOutsideGap = 6
		iInsideGap = 10
		iBetweenGap = iOutsideGap - 2
		iHeaderHeight = 32

		# Header
		headerBackgroundPanelName = self.getNextWidgetName()
		iLeft = iOutsideGap
		iTop = 50 + iOutsideGap
		iWidth = self.W_SCREEN - (2 * iOutsideGap)
		iHeight = iHeaderHeight + (2 * iInsideGap)
		screen.addPanel(headerBackgroundPanelName, "", "", True, False, iLeft, iTop, iWidth, iHeight, PanelStyles.PANEL_STYLE_MAIN)

		headerPanelName = self.getNextWidgetName()
		iLeft = iLeft + iInsideGap
		iTop = iTop + iInsideGap
		iWidth = iWidth - (2 * iInsideGap)
		iHeight = iHeaderHeight
		screen.addPanel(headerPanelName, "", "", False, True, iLeft, iTop, iWidth, iHeight, PanelStyles.PANEL_STYLE_EMPTY)

		iOffset = 0

		if FavoriteCivicDetector.isDetectionNecessary():
			fcHeaderText = BugUtil.getPlainText("TXT_KEY_FOREIGN_ADVISOR_POSSIBLE_FAV_CIVICS")
		else:
			fcHeaderText = BugUtil.getPlainText("TXT_KEY_PEDIA_FAV_CIVIC")
		
		for headerText in (BugUtil.getPlainText("TXT_KEY_FOREIGN_ADVISOR_ABBR_LEADER"),
						   BugUtil.getPlainText("TXT_KEY_FOREIGN_ADVISOR_ABBR_ATTITUDE"),
						   u"%c" %(CyGame().getSymbolID(FontSymbols.RELIGION_CHAR)), 
						   u"%c" %(CyGame().getSymbolID(FontSymbols.TRADE_CHAR)),
						   u"%c%c" %(CyGame().getSymbolID(FontSymbols.TRADE_CHAR),gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar()),
						   BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_GOVERNMENT"),
						   BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_LEGAL"),
						   BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_LABOR"),
						   BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_ECONOMY"),
						   BugUtil.getPlainText("TXT_KEY_CIVICOPTION_ABBR_RELIGION"),
						   "",
						   fcHeaderText):
			itemName = self.getNextWidgetName()
			screen.attachTextGFC(headerPanelName, itemName, headerText, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)
			iOffset = iOffset + 65

		# Main
		mainBackgroundPanelName = self.getNextWidgetName()
		iLeft = iOutsideGap
		iTop = iTop + iHeaderHeight + iInsideGap + iBetweenGap
		iWidth = self.W_SCREEN - (2 * iOutsideGap)
		iHeight = self.H_SCREEN - 100 - (2 * iOutsideGap) - iBetweenGap - iHeaderHeight - (2 * iInsideGap)
		screen.addPanel(mainBackgroundPanelName, "", "", True, False, iLeft, iTop, iWidth, iHeight, PanelStyles.PANEL_STYLE_MAIN)

		mainPanelName = self.getNextWidgetName()
		iLeft = iLeft + iInsideGap
		iTop = iTop + iInsideGap
		iWidth = iWidth - (2 * iInsideGap)
		iHeight = iHeight - (2 * iInsideGap)
		screen.addPanel(mainPanelName, "", "", True, True, iLeft, iTop, iWidth, iHeight, PanelStyles.PANEL_STYLE_EMPTY)

		FavoriteCivicDetector.doUpdate()
		
		# display the active player's row at the top
		self.drawInfoRow(screen, mainPanelName, self.iActiveLeader, PanelStyles.PANEL_STYLE_MAIN_BLACK25)

		# loop through all other players and add their rows; show known first
		lKnownPlayers = []
		lUnknownPlayers = []
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			if (iLoopPlayer != self.iActiveLeader):
				objLoopPlayer = gc.getPlayer(iLoopPlayer)
				if (self.objActiveTeam.isHasMet(objLoopPlayer.getTeam()) or gc.getGame().isDebugMode()):
					lKnownPlayers.append(iLoopPlayer)
				else:
					lUnknownPlayers.append(iLoopPlayer)
		for iLoopPlayer in lKnownPlayers:
			self.drawInfoRow(screen, mainPanelName, iLoopPlayer, PanelStyles.PANEL_STYLE_OUT)
		for iLoopPlayer in lUnknownPlayers:
			self.drawInfoRow(screen, mainPanelName, iLoopPlayer, PanelStyles.PANEL_STYLE_OUT)

	def drawInfoRow (self, screen, mainPanelName, iLoopPlayer, ePanelStyle):
		objLoopPlayer = gc.getPlayer(iLoopPlayer)
		iLoopTeam = objLoopPlayer.getTeam()
		objLoopTeam = gc.getTeam(iLoopTeam)
		bIsActivePlayer = (iLoopPlayer == self.iActiveLeader)
		if (objLoopPlayer.isAlive()
			#and (self.objActiveTeam.isHasMet(iLoopTeam) or gc.getGame().isDebugMode())
			and not objLoopPlayer.isBarbarian()
			and not objLoopPlayer.isMinorCiv()):
			
			objLeaderHead = gc.getLeaderHeadInfo (objLoopPlayer.getLeaderType())
			objAttitude = AttitudeUtil.Attitude(iLoopPlayer, self.iActiveLeader)

			# Player panel
			playerPanelName = self.getNextWidgetName()
			szPlayerLabel = "" # objLoopPlayer.getName()
			screen.attachPanel(mainPanelName, playerPanelName, szPlayerLabel, "", False, True, ePanelStyle)

			# Panels always created but essentially blank if unmet
			itemName = self.getNextWidgetName()
			if (not self.objActiveTeam.isHasMet(iLoopTeam) and not gc.getGame().isDebugMode()):
				screen.attachImageButton(playerPanelName, itemName, gc.getDefineSTRING("LEADERHEAD_RANDOM"), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_GENERAL, -1, -1, False)
				return
			else:
				screen.attachImageButton(playerPanelName, itemName, objLeaderHead.getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader, False)
			#screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)
					
			infoPanelName = self.getNextWidgetName()
			screen.attachPanel(playerPanelName, infoPanelName, "", "", False, False, PanelStyles.PANEL_STYLE_EMPTY)

			# Attitude
			itemName = self.getNextWidgetName()
			if (not bIsActivePlayer):
				szAttStr = "<font=2>" + objAttitude.getText(True, True, False, False) + "</font>"
			else:
				szAttStr = ""
			screen.attachTextGFC(infoPanelName, itemName, szAttStr, FontTypes.GAME_FONT, 
								*BugDll.widgetVersion(2, "WIDGET_LEADERHEAD_RELATIONS", iLoopPlayer, self.iActiveLeader, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader))
			# Disable the widget if this is active player since it's a blank string.
			if bIsActivePlayer:
				screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)

			# Religion
			itemName = self.getNextWidgetName()
			nReligion = objLoopPlayer.getStateReligion()
			if (nReligion != -1):
				objReligion = gc.getReligionInfo (nReligion)

				if (objLoopPlayer.hasHolyCity (nReligion)):
					szPlayerReligion = u"%c" %(objReligion.getHolyCityChar())
				elif objReligion:
					szPlayerReligion = u"%c" %(objReligion.getChar())

				if (not bIsActivePlayer):
					iDiploModifier = 0
					if (nReligion == self.objActiveLeader.getStateReligion()):
						iDiploModifier = objAttitude.getModifier("TXT_KEY_MISC_ATTITUDE_SAME_RELIGION")
					else:
						iDiploModifier = objAttitude.getModifier("TXT_KEY_MISC_ATTITUDE_DIFFERENT_RELIGION")
					if (iDiploModifier):
						if (iDiploModifier > 0):
							szColor = "COLOR_GREEN"
						else:
							szColor = "COLOR_RED"
						szPlayerReligion = localText.changeTextColor(szPlayerReligion + " [%+d]" % (iDiploModifier), gc.getInfoTypeForString(szColor))
				szPlayerReligion = "<font=2>" + szPlayerReligion + "</font>"
			else:
				szPlayerReligion = ""
			
			screen.attachTextGFC(infoPanelName, itemName, szPlayerReligion, FontTypes.GAME_FONT, 
								*BugDll.widgetVersion(2, "WIDGET_LEADERHEAD_RELATIONS", iLoopPlayer, self.iActiveLeader, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader))
			# Disable the widget if this is active player since we don't have diplo info.
			if bIsActivePlayer:
				screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)
			
			# Trade
			if (bIsActivePlayer or objLoopPlayer.canHaveTradeRoutesWith(self.iActiveLeader)):
				(iTradeCommerce, iTradeRoutes) = self.calculateTrade (self.iActiveLeader, iLoopPlayer)
				if TradeUtil.isFractionalTrade():
					iTradeCommerce //= 100
				szTradeYield = u"%d %c" % (iTradeCommerce, gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar())
				szTradeRoutes = u"%d" % (iTradeRoutes)
			else:
				szTradeYield = u"-"
				szTradeRoutes = u"-"
			itemName = self.getNextWidgetName()
			screen.attachTextGFC(infoPanelName, itemName, szTradeRoutes, FontTypes.GAME_FONT, 
								 *BugDll.widget("WIDGET_TRADE_ROUTES", self.iActiveLeader, iLoopPlayer))
			if not BugDll.isPresent():
				# Trade has no useful widget so disable hit testing.
				screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)
			itemName = self.getNextWidgetName()
			screen.attachTextGFC(infoPanelName, itemName, szTradeYield, FontTypes.GAME_FONT, 
								 *BugDll.widget("WIDGET_TRADE_ROUTES", self.iActiveLeader, iLoopPlayer))
			if not BugDll.isPresent():
				# Trade has no useful widget so disable hit testing.
				screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)
			
			# Civics
			for nCivicOption in range (gc.getNumCivicOptionInfos()):
				nCivic = objLoopPlayer.getCivics (nCivicOption)
				buttonName = self.getNextWidgetName()
				screen.attachImageButton (infoPanelName, buttonName, gc.getCivicInfo (nCivic).getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nCivic, 1, False)

			# Spacer so Favorite Civics aren't right next to current civics
			screen.attachTextGFC(infoPanelName, "", " ", FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
			
			# Favorite Civic
			if (not bIsActivePlayer):
				nFavoriteCivic = objLeaderHead.getFavoriteCivic()
				if FavoriteCivicDetector.isDetectionNecessary():
					objFavorite = FavoriteCivicDetector.getFavoriteCivicInfo(iLoopPlayer)
					if objFavorite.isKnown():
						# We know it. Fall through to standard procedure after setting it.
						nFavoriteCivic = objFavorite.getFavorite()
					else:
						iNumPossibles = objFavorite.getNumPossibles()
						BugUtil.debug("CvExoticForeignAdvisor::drawInfoRows() Number of Guesses: %d" %(iNumPossibles))
						if iNumPossibles > 5:
							# Too many possibilities; display question mark
							screen.attachImageButton (infoPanelName, "", "Art/BUG/QuestionMark.dds", GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_GENERAL, -1, -1, False)
							return
						else:
							# Loop over possibles and display all
							for nFavoriteCivic in objFavorite.getPossibles():
								objCivicInfo = gc.getCivicInfo (nFavoriteCivic)
								screen.attachImageButton (infoPanelName, "", objCivicInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nFavoriteCivic, 1, False)
							return
					
				if nFavoriteCivic != -1:
					objCivicInfo = gc.getCivicInfo (nFavoriteCivic)
					screen.attachImageButton (infoPanelName, "", objCivicInfo.getButton(), GenericButtonSizes.BUTTON_SIZE_46, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, nFavoriteCivic, 1, False)
					if (self.objActiveLeader.isCivic (nFavoriteCivic)):
						iDiploModifier = objAttitude.getModifier("TXT_KEY_MISC_ATTITUDE_FAVORITE_CIVIC")
						if (iDiploModifier):
							if (iDiploModifier > 0):
								szColor = "COLOR_GREEN"
							else:
								szColor = "COLOR_RED"
							szDiplo = "<font=2>" + localText.changeTextColor(" [%+d]" % (iDiploModifier), gc.getInfoTypeForString(szColor)) + "</font>"
						else:
							szDiplo = ""
						itemName = self.getNextWidgetName()
						screen.attachTextGFC(infoPanelName, itemName, szDiplo, FontTypes.GAME_FONT, 
								*BugDll.widgetVersion(2, "WIDGET_LEADERHEAD_RELATIONS", iLoopPlayer, self.iActiveLeader, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader))
						#screen.setHitTest(itemName, HitTestTypes.HITTEST_NOHIT)

	def calculateTrade (self, nPlayer, nTradePartner):
		# Trade status...
		iDomesticYield, iDomesticCount, iForeignYield, iForeignCount = TradeUtil.calculateTradeRoutes(nPlayer, nTradePartner)
		return iDomesticYield + iForeignYield, iDomesticCount + iForeignCount

	def drawGlance (self, bInitial):
#		ExoticForPrint ("Entered drawGlance")

		screen = self.getScreen()
		iActiveTeam = gc.getPlayer(self.iActiveLeader).getTeam()

		# Put everything inside a main panel, so we get vertical scrolling
		headerPanelName = self.getNextWidgetName()
		screen.addPanel(headerPanelName, "", "", True, True, 0, 50, self.W_SCREEN, 60, PanelStyles.PANEL_STYLE_TOPBAR)

		if (bInitial):
			self.initializeGlance()
			self.iSelectedLeader = self.iActiveLeader
		
		self.nSpread = self.W_SCREEN / self.nCount
		self.drawGlanceHeader(screen, headerPanelName)

		mainPanelName = self.getNextWidgetName()
		screen.addPanel(mainPanelName, "", "", True, True, 0, 104, self.W_SCREEN, self.H_SCREEN - 155, PanelStyles.PANEL_STYLE_MAIN)

		self.drawGlanceRows (screen, mainPanelName, self.iSelectedLeader != self.iActiveLeader, self.iSelectedLeader)

	def calculateRelations (self, nPlayer, nTarget):
		if (nPlayer != nTarget and gc.getTeam(gc.getPlayer(nPlayer).getTeam()).isHasMet(gc.getPlayer(nTarget).getTeam())):
			nAttitude = 0
			szAttitude = CyGameTextMgr().getAttitudeString(nPlayer, nTarget)
			ltPlusAndMinuses = re.findall ("[-+][0-9]+\s?: ", szAttitude)
			for i in range (len (ltPlusAndMinuses)):
				nAttitude += int (ltPlusAndMinuses[i][:-2])
		else:
			return None
		return nAttitude		
		
	def initializeGlance (self):
		self.nCount = 0
		self.ltPlayerRelations = [[0] * gc.getMAX_PLAYERS() for i in range (gc.getMAX_PLAYERS())]
		self.ltPlayerMet = [False] * gc.getMAX_PLAYERS()

		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			if (gc.getPlayer(iLoopPlayer).isAlive()
			and (gc.getTeam(gc.getPlayer(iLoopPlayer).getTeam()).isHasMet(gc.getPlayer(self.iActiveLeader).getTeam())
			or gc.getGame().isDebugMode())
			and not gc.getPlayer(iLoopPlayer).isBarbarian()
			and not gc.getPlayer(iLoopPlayer).isMinorCiv()):

#				ExoticForPrint ("Player = %d" % iLoopPlayer)
				self.ltPlayerMet [iLoopPlayer] = True

				for nHost in range(gc.getMAX_PLAYERS()):
					if (gc.getPlayer(nHost).isAlive()
					and nHost != self.iActiveLeader
					and (gc.getTeam(gc.getPlayer(nHost).getTeam()).isHasMet(gc.getPlayer(self.iActiveLeader).getTeam())
					or gc.getGame().isDebugMode())
					and not gc.getPlayer(nHost).isBarbarian()
					and not gc.getPlayer(nHost).isMinorCiv()):
						nRelation = AttitudeUtil.getAttitudeCount(nHost, iLoopPlayer)
						self.ltPlayerRelations [iLoopPlayer][nHost] = nRelation

				# Player panel
				self.nCount += 1

		self.X_Spread = (self.W_SCREEN - 20) / self.nCount
		if self.X_Spread < 58: self.X_Spread = 58

		self.Y_Spread = (self.H_SCREEN - 50) / (self.nCount + 2)
		self.Y_Text_Offset = (self.Y_Spread - 36) / 2
		if self.Y_Text_Offset < 0: self.Y_Text_Offset = 0

	def drawGlanceHeader (self, screen, panelName):
		nCount = 1
		for iLoopPlayer in range (gc.getMAX_PLAYERS()):
			if self.ltPlayerMet[iLoopPlayer]:
				if (iLoopPlayer != self.iActiveLeader):
					szName = self.getNextWidgetName()
					screen.addCheckBoxGFCAt(panelName, szName, gc.getLeaderHeadInfo(gc.getPlayer(iLoopPlayer).getLeaderType()).getButton(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_GLANCE_OFFSET + (self.X_Spread * nCount), self.Y_GLANCE_OFFSET, self.GLANCE_BUTTON_SIZE, self.GLANCE_BUTTON_SIZE, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader, ButtonStyles.BUTTON_STYLE_LABEL, False)
					if (self.iSelectedLeader == iLoopPlayer):
						screen.setState(szName, True)
					else:
						screen.setState(szName, False)
					nCount += 1
		
	def drawGlanceRows (self, screen, mainPanelName, bSorted = False, nPlayer = 1):
#		ExoticForPrint ("MAX Players = %d" % gc.getMAX_PLAYERS())
		iPanelHeight = max(self.GLANCE_BUTTON_SIZE, ((self.H_SCREEN - 110 - self.GLANCE_BUTTON_SIZE) / self.nCount - 5))
		ltSortedRelations = [(None,-1)] * gc.getMAX_PLAYERS()
		self.loadColIntoList (self.ltPlayerRelations, ltSortedRelations, nPlayer)
		if bSorted:
			ltSortedRelations.sort()
			if (self.bGlancePlus):
				ltSortedRelations.reverse()
			self.bGlancePlus = not self.bGlancePlus
		else:
			# If not sorted, we take the original ID list and move active player to the front.
			#ltSortedRelations = map(lambda x: (0, x), range(gc.getMAX_PLAYERS()))
			nFirstElement = self.ltPlayerRelations[self.iActiveLeader][nPlayer]
			ltSortedRelations.remove((nFirstElement, self.iActiveLeader))
			ltSortedRelations.insert(0, (nFirstElement, self.iActiveLeader))

		# loop through all players and display leaderheads
		for nOffset in range (gc.getMAX_PLAYERS()):
			if ltSortedRelations[nOffset][1] != -1:
				break

		for i in range (self.nCount):
			iLoopPlayer = ltSortedRelations[nOffset + i][1]
#			ExoticForPrint ("iLoopPlayer = %d" % iLoopPlayer)

			playerPanelName = self.getNextWidgetName()
			if iLoopPlayer == self.iActiveLeader:
				screen.attachPanel(mainPanelName, playerPanelName, "", "", False, True, PanelStyles.PANEL_STYLE_MAIN_BLACK50)
			else:
				screen.attachPanel(mainPanelName, playerPanelName, "", "", False, True, PanelStyles.PANEL_STYLE_MAIN_BLACK25)

			szName = self.getNextWidgetName()
			screen.attachCheckBoxGFC(playerPanelName, szName, gc.getLeaderHeadInfo(gc.getPlayer(iLoopPlayer).getLeaderType()).getButton(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.GLANCE_BUTTON_SIZE, self.GLANCE_BUTTON_SIZE, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader, ButtonStyles.BUTTON_STYLE_LABEL)
## War Attitude Info ##
			nCount = 0
			for j in xrange (gc.getMAX_PLAYERS()):
				if self.ltPlayerMet[j]:
					if j != self.iActiveLeader:
						szName = self.getNextWidgetName()
						szName2 = self.getNextWidgetName()
						nAttitude = self.ltPlayerRelations[iLoopPlayer][j]
						if nAttitude != None:
							if gc.getTeam(gc.getPlayer(j).getTeam()).canDeclareWar(gc.getPlayer(iLoopPlayer).getTeam()) and not gc.getPlayer(j).isHuman():
								iLeaderType = gc.getPlayer(j).getLeaderType()
								iNoWar = gc.getLeaderHeadInfo(iLeaderType).getNoWarAttitudeProb(gc.getPlayer(j).AI_getAttitude(iLoopPlayer))
								sColor = CyTranslator().getText("[COLOR_RED]", ())
								if iNoWar > 80:
									sColor = CyTranslator().getText("[COLOR_GREEN]", ())
								elif iNoWar > 60:
									sColor = CyTranslator().getText("[COLOR_CYAN]", ())
								elif iNoWar > 40:
									sColor = CyTranslator().getText("[COLOR_WHITE]", ())
								elif iNoWar > 20:
									sColor = CyTranslator().getText("[COLOR_MAGENTA]", ())
							
								szText = "<font=3>" + sColor + str(iNoWar) + "%</color></font>"
								screen.setTextAt (szName2, playerPanelName, szText, CvUtil.FONT_CENTER_JUSTIFY, self.X_GLANCE_OFFSET + (self.nSpread * nCount), iPanelHeight/8, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_PYTHON, 3838, iLeaderType)
							szText = self.getAttitudeText (nAttitude, j, iLoopPlayer)
							screen.setTextAt (szName, playerPanelName, szText, CvUtil.FONT_CENTER_JUSTIFY, self.X_GLANCE_OFFSET + (self.nSpread * nCount), iPanelHeight /2 - 5, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_LEADERHEAD, j, iLoopPlayer)
						else:
							szText = CyTranslator().getText("TXT_KEY_FOREIGN_ADVISOR_NONE", ())
							screen.setTextAt (szName, playerPanelName, szText, CvUtil.FONT_CENTER_JUSTIFY, self.X_GLANCE_OFFSET + (self.nSpread * nCount), iPanelHeight /2 - 10, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
					nCount += 1
## War Attitude Info ##

	def loadColIntoList (self, ltPlayers, ltTarget, nCol):
		nCount = 0
		for i in xrange (len (ltTarget)):
			if (self.ltPlayerMet[i]):
#				ExoticForPrint ("player met = %d; nCount = %d" % (i, nCount))
				ltTarget[nCount] = (ltPlayers[i][nCol], i)
				nCount += 1

	def getAttitudeText (self, nAttitude, nPlayer, nTarget):
		szText = str (nAttitude)
		szAttitude = CyGameTextMgr().getAttitudeString(nPlayer, nTarget)
		if nAttitude > 0:
			szText = "+" + szText
		for szColor, szSearchString in self.ATTITUDE_DICT.items():
			if re.search (szSearchString, szAttitude):
				color = gc.getInfoTypeForString(szColor)
				szText = CyTranslator().changeTextColor (szText, color)
		szText = "<font=4>" + szText + "</font>"
		return szText

	def handlePlusMinusToggle (self):
#		ExoticForPrint ("Entered handlePlusMinusToggle")

		self.bGlancePlus = not self.bGlancePlus
		self.drawContents (False)

############################################
### BEGIN CHANGES ENHANCED INTERFACE MOD ###
############################################

	def initTradeTable(self):
		screen = self.getScreen()
		
		if (self.RES_SHOW_ACTIVE_TRADE):
			columns = ( IconGrid_BUG.GRID_ICON_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN
					  , IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_TEXT_COLUMN
					  , IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_TEXT_COLUMN )
		else:
			columns = ( IconGrid_BUG.GRID_ICON_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN
					  , IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_MULTI_LIST_COLUMN, IconGrid_BUG.GRID_TEXT_COLUMN )
		self.NUM_RESOURCE_COLUMNS = len(columns) - 1
		
		gridX = self.MIN_LEFT_RIGHT_SPACE + 10
		gridY = self.MIN_TOP_BOTTOM_SPACE + self.RES_SURPLUS_HEIGHT + self.RES_PANEL_SPACE + self.TITLE_HEIGHT + 10
		gridWidth = self.W_SCREEN - self.MIN_LEFT_RIGHT_SPACE * 2 - 20
		gridHeight = self.H_SCREEN - self.MIN_TOP_BOTTOM_SPACE * 2 - self.RES_SURPLUS_HEIGHT - self.RES_PANEL_SPACE - self.TITLE_HEIGHT - 20
		
		self.resIconGridName = self.getNextWidgetName()
		self.resIconGrid = IconGrid_BUG.IconGrid_BUG( self.resIconGridName, screen, gridX, gridY, gridWidth, gridHeight
											, columns, True, self.SHOW_LEADER_NAMES, self.SHOW_ROW_BORDERS )

		self.resIconGrid.setGroupBorder(self.GROUP_BORDER)
		self.resIconGrid.setGroupLabelOffset(self.GROUP_LABEL_OFFSET)
		self.resIconGrid.setMinColumnSpace(self.MIN_COLUMN_SPACE)
		self.resIconGrid.setMinRowSpace(self.MIN_ROW_SPACE)
		
		self.leaderCol = 0
		self.surplusCol = 1
		self.usedCol = 2
		self.willTradeCol = 3
		self.wontTradeCol = 4
		self.canPayCol = 5
		self.activeExportCol = 6
		self.activeImportCol = 7
		self.payingCol = 8
		
		self.resIconGrid.setHeader( self.leaderCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_LEADER", ()) )
		self.resIconGrid.setHeader( self.surplusCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_FOR_TRADE_2", ()) )
		self.resIconGrid.setHeader( self.usedCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_NOT_FOR_TRADE_2", ()) )
		self.resIconGrid.setHeader( self.willTradeCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_FOR_TRADE_2", ()) )
		self.resIconGrid.setHeader( self.wontTradeCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_NOT_FOR_TRADE_2", ()) )
		self.resIconGrid.setHeader( self.canPayCol, (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()) )
		self.resIconGrid.setTextColWidth(self.canPayCol, self.RES_GOLD_COL_WIDTH)
		
		if (self.RES_SHOW_ACTIVE_TRADE):
			self.resIconGrid.setHeader( self.activeExportCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_EXPORT", ()) )
			self.resIconGrid.setHeader( self.activeImportCol, localText.getText("TXT_KEY_FOREIGN_ADVISOR_IMPORT", ()) )
			self.resIconGrid.setHeader( self.payingCol, (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()) )
			self.resIconGrid.setTextColWidth(self.payingCol, self.RES_GOLD_COL_WIDTH)
		if (self.RES_SHOW_IMPORT_EXPORT_HEADER):
			self.resIconGrid.createColumnGroup("", 1)
			self.resIconGrid.createColumnGroup(localText.getText("TXT_KEY_FOREIGN_ADVISOR_EXPORT", ()), 2)
			self.resIconGrid.createColumnGroup(localText.getText("TXT_KEY_FOREIGN_ADVISOR_IMPORT", ()), 3)
			if (self.RES_SHOW_ACTIVE_TRADE):
				self.resIconGrid.createColumnGroup(localText.getText("TXT_KEY_FOREIGN_ADVISOR_ACTIVE", ()), 3)
		
		gridWidth = self.resIconGrid.getPrefferedWidth()
		gridHeight = self.resIconGrid.getPrefferedHeight()
		self.RES_LEFT_RIGHT_SPACE = (self.W_SCREEN - gridWidth - 20) / 2
		self.RES_TOP_BOTTOM_SPACE = (self.H_SCREEN - gridHeight - self.RES_SURPLUS_HEIGHT - self.RES_PANEL_SPACE - self.TITLE_HEIGHT - 20) / 2
		gridX = self.RES_LEFT_RIGHT_SPACE + 10
		gridY = self.RES_TOP_BOTTOM_SPACE + self.RES_SURPLUS_HEIGHT + self.RES_PANEL_SPACE + self.TITLE_HEIGHT + 10
		
		self.resIconGrid.setPosition(gridX, gridY)
		self.resIconGrid.setSize(gridWidth, gridHeight)
# 		self.RES_LEFT_RIGHT_SPACE = self.MIN_LEFT_RIGHT_SPACE
# 		self.RES_TOP_BOTTOM_SPACE = self.MIN_TOP_BOTTOM_SPACE

	
## Platy Bonus Screen ##		
	def calculateSurplusPanelLayout(self):
		self.SURPLUS_X = self.RES_LEFT_RIGHT_SPACE
		self.SURPLUS_Y = self.RES_TOP_BOTTOM_SPACE
		self.SURPLUS_WIDTH = self.W_SCREEN - 2 * self.RES_LEFT_RIGHT_SPACE
		
		self.SURPLUS_ICONS_X = self.SURPLUS_X + 10
		iNumRows = self.RES_SURPLUS_HEIGHT/ self.RESOURCE_ICON_SIZE -1
		if (self.RES_SHOW_SURPLUS_AMOUNT_ON_TOP):
			self.SURPLUS_TABLE_X = self.SURPLUS_ICONS_X + 15
			SURPLUS_VERTICAL_SPACING = (self.RES_SURPLUS_HEIGHT - iNumRows *self.RESOURCE_ICON_SIZE - self.TITLE_HEIGHT) / 2
			self.SURPLUS_ICONS_Y = self.SURPLUS_Y + SURPLUS_VERTICAL_SPACING + self.TITLE_HEIGHT
			self.SURPLUS_TABLE_Y = self.SURPLUS_ICONS_Y + (self.RESOURCE_ICON_SIZE - self.TABLE_CONTROL_HEIGHT) / 2 + 8
		else:
			self.SURPLUS_TABLE_X = self.SURPLUS_ICONS_X + 5
			SURPLUS_VERTICAL_SPACING = ( self.RES_SURPLUS_HEIGHT - (iNumRows *self.RESOURCE_ICON_SIZE) - self.TABLE_CONTROL_HEIGHT 
									   - self.TITLE_HEIGHT ) / 2 + 3
			self.SURPLUS_ICONS_Y = self.SURPLUS_Y + SURPLUS_VERTICAL_SPACING + self.TITLE_HEIGHT
			self.SURPLUS_TABLE_Y = self.SURPLUS_ICONS_Y + self.RESOURCE_ICON_SIZE
		
		self.SURPLUS_CIRCLE_X_START = self.SURPLUS_TABLE_X + 4
		self.SURPLUS_CIRCLE_Y = self.SURPLUS_TABLE_Y + 5
## Platy Bonus Screen ##		

		
	def drawResourceDeals(self, bInitial):
		screen = self.getScreen()
		activePlayer = gc.getPlayer(self.iActiveLeader)
		self.initTradeTable()
		
		# Find all the surplus resources
		tradeData = TradeData()
		tradeData.ItemType = TradeableItems.TRADE_RESOURCES
## Surplus Type Start ##
		self.SURPLUS_WIDTH = self.W_SCREEN - 2 * self.RES_LEFT_RIGHT_SPACE
		
		# Assemble the surplus panel
		self.mainAvailablePanel = self.getNextWidgetName()
#		self.calculateSurplusPanelLayout()
		szDropdownName = str("PlatySurplus")
		screen.addDropDownBoxGFC(szDropdownName, self.RES_LEFT_RIGHT_SPACE + 160, self.RES_TOP_BOTTOM_SPACE - 5, 100, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_ALL",()), 0, 0, True)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_PEDIA_GENERAL",()), 1, 1, 0 == self.iSurplus)
		iBonusClass = 1
		while not gc.getBonusClassInfo(iBonusClass) is None:
			sText = gc.getBonusClassInfo(iBonusClass).getType()
			sText = sText[sText.find("_") +1:]
			sText = sText.lower()
			sText = sText.capitalize()
			screen.addPullDownString(szDropdownName, sText, iBonusClass + 1, iBonusClass + 1, iBonusClass == self.iSurplus)
			iBonusClass += 1

		listSurplus = []
		
		for iLoopBonus in xrange(gc.getNumBonusInfos()):
			if (gc.getBonusInfo(iLoopBonus).getBonusClassType() != self.iSurplus) and self.iSurplus > -1: continue
			tradeData.iData = iLoopBonus
			if activePlayer.getNumTradeableBonuses(iLoopBonus) < 2: continue
			for iLoopPlayer in xrange(gc.getMAX_CIV_PLAYERS()):
				currentPlayer = gc.getPlayer(iLoopPlayer)
				if currentPlayer.isMinorCiv(): continue
				if iLoopPlayer == self.iActiveLeader: continue
				if not currentPlayer.isAlive(): continue
				if gc.getTeam(currentPlayer.getTeam()).isHasMet(activePlayer.getTeam()) and activePlayer.canTradeItem(iLoopPlayer, tradeData, False):
					listSurplus.append(iLoopBonus)
					break
## Surplus Type End ##
		
## Platy Bonus Screen ##
		if len(listSurplus) > 0:
			self.availableTable = self.getNextWidgetName()
			iColumnWidth = 70
			iMaxColumn = self.SURPLUS_WIDTH / iColumnWidth
			iWidthSpace = (self.SURPLUS_WIDTH - (iMaxColumn * iColumnWidth)) /2
			iTable_Y = self.RES_TOP_BOTTOM_SPACE + 25
			iTable_H = self.RES_SURPLUS_HEIGHT - 50
#			if self.PanelStyle == PanelStyles.PANEL_STYLE_MAIN:
#				iTable_Y = self.RES_TOP_BOTTOM_SPACE + 36
#				iTable_H = self.RES_SURPLUS_HEIGHT - 48
			screen.addTableControlGFC(self.availableTable, iMaxColumn, self.RES_LEFT_RIGHT_SPACE + iWidthSpace, iTable_Y, iMaxColumn * (iColumnWidth), iTable_H
				    , False, True, 24, 24, TableStyles.TABLE_STYLE_EMPTY )

			for i in xrange(iMaxColumn):
				screen.setTableColumnHeader(self.availableTable, i, "", iColumnWidth)
			nRows = (len(listSurplus) + iMaxColumn - 1) / iMaxColumn
			for i in xrange(nRows):
				screen.appendTableRow(self.availableTable)

			for i in xrange(len(listSurplus)):
				iRow = i / iMaxColumn
				iColumn = i % iMaxColumn
				sText = u"<font=4>%c<font=1> (%d)</font>" %(gc.getBonusInfo(listSurplus[i]).getChar(), activePlayer.getNumTradeableBonuses(listSurplus[i]) - 1)
				screen.setTableText(self.availableTable, iColumn, iRow, sText, "", WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, listSurplus[i], 1, CvUtil.FONT_LEFT_JUSTIFY )
## Platy Bonus Screen ##	
		
		
		
# 		# Assemble the panel that shows the trade table
		self.TABLE_PANEL_X = self.RES_LEFT_RIGHT_SPACE
		self.TABLE_PANEL_Y = self.RES_TOP_BOTTOM_SPACE + self.RES_SURPLUS_HEIGHT
		self.TABLE_PANEL_WIDTH = self.W_SCREEN - 2 * self.RES_LEFT_RIGHT_SPACE
		self.TABLE_PANEL_HEIGHT = self.H_SCREEN - self.TABLE_PANEL_Y - self.RES_TOP_BOTTOM_SPACE
		
		self.tradePanel = self.getNextWidgetName()
		screen.addPanel( self.tradePanel, localText.getText("TXT_KEY_FOREIGN_ADVISOR_TRADE_TABLE", ()), ""
					   , True, True, self.TABLE_PANEL_X, self.TABLE_PANEL_Y, self.TABLE_PANEL_WIDTH, self.TABLE_PANEL_HEIGHT
					   , PanelStyles.PANEL_STYLE_MAIN )
		
		self.resIconGrid.createGrid()
		
		# find all players that need to be listed 
		self.resIconGrid.clearData()
		tradeData = TradeData()
		tradeData.ItemType = TradeableItems.TRADE_RESOURCES
		currentRow = 0
		
		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			currentPlayer = gc.getPlayer(iLoopPlayer)
			if ( currentPlayer.isAlive() and not currentPlayer.isBarbarian() and not currentPlayer.isMinorCiv() 
										 and gc.getTeam(currentPlayer.getTeam()).isHasMet(activePlayer.getTeam()) 
										 and iLoopPlayer != self.iActiveLeader ):
				message = ""
				if ( not activePlayer.canTradeNetworkWith(iLoopPlayer) ):
					message = localText.getText("TXT_KEY_FOREIGN_ADVISOR_NOT_CONNECTED", ())
				
				self.resIconGrid.appendRow(currentPlayer.getName(), message)
				self.resIconGrid.addIcon( currentRow, self.leaderCol
										, gc.getLeaderHeadInfo(currentPlayer.getLeaderType()).getButton()
										, 64, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader )

				# gold
				if (gc.getTeam(activePlayer.getTeam()).isGoldTrading() or gc.getTeam(currentPlayer.getTeam()).isGoldTrading()):
					sAmount = str(gc.getPlayer(iLoopPlayer).AI_maxGoldPerTurnTrade(self.iActiveLeader))
					self.resIconGrid.setText(currentRow, self.canPayCol, sAmount)
				
				# bonuses
				for iLoopBonus in range(gc.getNumBonusInfos()):
## Surplus Type ##
					if (gc.getBonusInfo(iLoopBonus).getBonusClassType() != self.iSurplus) and self.iSurplus > -1: continue
## Surplus Type ##					
					tradeData.iData = iLoopBonus
					if (activePlayer.canTradeItem(iLoopPlayer, tradeData, False)):
						if (activePlayer.canTradeItem(iLoopPlayer, tradeData, (not currentPlayer.isHuman()))): # surplus
							self.resIconGrid.addIcon( currentRow, self.surplusCol, gc.getBonusInfo(iLoopBonus).getButton()
													, 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iLoopBonus )
						else: # used
							self.resIconGrid.addIcon( currentRow, self.usedCol, gc.getBonusInfo(iLoopBonus).getButton()
													, 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iLoopBonus )
					if (currentPlayer.canTradeItem(self.iActiveLeader, tradeData, False)):
						if (currentPlayer.canTradeItem(self.iActiveLeader, tradeData, (not currentPlayer.isHuman()))): # will trade
							self.resIconGrid.addIcon( currentRow, self.willTradeCol, gc.getBonusInfo(iLoopBonus).getButton()
													, 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iLoopBonus )
						else: # won't trade
							self.resIconGrid.addIcon( currentRow, self.wontTradeCol, gc.getBonusInfo(iLoopBonus).getButton()
													, 64, *BugDll.widget("WIDGET_PEDIA_JUMP_TO_BONUS_TRADE", iLoopBonus, iLoopPlayer, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iLoopBonus, -1) )
				if (self.RES_SHOW_ACTIVE_TRADE):
					amount = 0
					for iLoopDeal in range(gc.getGame().getIndexAfterLastDeal()):
						deal = gc.getGame().getDeal(iLoopDeal)
# BUG - Kill Deal - start
						if not deal.isNone():
							if ( deal.getFirstPlayer() == iLoopPlayer and deal.getSecondPlayer() == self.iActiveLeader):
								for iLoopTradeItem in range(deal.getLengthFirstTrades()):
									tradeData2 = deal.getFirstTrade(iLoopTradeItem)
									if (tradeData2.ItemType == TradeableItems.TRADE_GOLD_PER_TURN):
										amount += tradeData2.iData
									if (tradeData2.ItemType == TradeableItems.TRADE_RESOURCES):
										self.resIconGrid.addIcon( currentRow, self.activeImportCol
																, gc.getBonusInfo(tradeData2.iData).getButton()
																, 64, *BugDll.widgetVersion(4, WidgetTypes.WIDGET_DEAL_KILL, iLoopDeal, iLoopTradeItem,
																							   WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, tradeData2.iData, -1) )
								for iLoopTradeItem in range(deal.getLengthSecondTrades()):
									tradeData2 = deal.getSecondTrade(iLoopTradeItem)
									if (tradeData2.ItemType == TradeableItems.TRADE_GOLD_PER_TURN):
										amount -= tradeData2.iData
									if (tradeData2.ItemType == TradeableItems.TRADE_RESOURCES):
										self.resIconGrid.addIcon( currentRow, self.activeExportCol
																, gc.getBonusInfo(tradeData2.iData).getButton()
																, 64, *BugDll.widgetVersion(4, WidgetTypes.WIDGET_DEAL_KILL, iLoopDeal, iLoopTradeItem + deal.getLengthFirstTrades(),
																							   WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, tradeData2.iData, -1) )
							
							if ( deal.getSecondPlayer() == iLoopPlayer and deal.getFirstPlayer() == self.iActiveLeader ):
								for iLoopTradeItem in range(deal.getLengthFirstTrades()):
									tradeData2 = deal.getFirstTrade(iLoopTradeItem)
									if (tradeData2.ItemType == TradeableItems.TRADE_GOLD_PER_TURN):
										amount -= tradeData2.iData
									if (tradeData2.ItemType == TradeableItems.TRADE_RESOURCES):
										self.resIconGrid.addIcon( currentRow, self.activeExportCol
																, gc.getBonusInfo(tradeData2.iData).getButton()
																, 64, *BugDll.widgetVersion(4, WidgetTypes.WIDGET_DEAL_KILL, iLoopDeal, iLoopTradeItem,
																							   WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, tradeData2.iData, -1) )
								for iLoopTradeItem in range(deal.getLengthSecondTrades()):
									tradeData2 = deal.getSecondTrade(iLoopTradeItem)
									if (tradeData2.ItemType == TradeableItems.TRADE_GOLD_PER_TURN):
										amount += tradeData2.iData
									if (tradeData2.ItemType == TradeableItems.TRADE_RESOURCES):
										self.resIconGrid.addIcon( currentRow, self.activeImportCol
																, gc.getBonusInfo(tradeData2.iData).getButton()
																, 64, *BugDll.widgetVersion(4, WidgetTypes.WIDGET_DEAL_KILL, iLoopDeal, iLoopTradeItem + deal.getLengthFirstTrades(),
																							   WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, tradeData2.iData, -1) )
# BUG - Kill Deal - end
					if (amount != 0):
						self.resIconGrid.setText(currentRow, self.payingCol, str(amount))
				currentRow += 1
		self.resIconGrid.refresh()
	
	
	def scrollTradeTableUp(self):
		if (self.iScreen == self.SCREEN_DICT["BONUS"]):
			self.resIconGrid.scrollUp()
		elif (self.iScreen == self.SCREEN_DICT["TECH"]):
			self.techIconGrid.scrollUp()


	def scrollTradeTableDown(self):
		if (self.iScreen == self.SCREEN_DICT["BONUS"]):
			self.resIconGrid.scrollDown()
		elif (self.iScreen == self.SCREEN_DICT["TECH"]):
			self.techIconGrid.scrollDown()
				
	def drawTechDeals(self, bInitial):
		screen = self.getScreen()
		activePlayer = gc.getPlayer(self.iActiveLeader)
		iActiveTeam = activePlayer.getTeam()
		activeTeam = gc.getTeam(iActiveTeam)

		self.initTechTable()

		# Assemble the panel
		TECH_PANEL_X = self.TECH_LEFT_RIGHT_SPACE
		TECH_PANEL_Y = self.TECH_TOP_BOTTOM_SPACE
		TECH_PANEL_WIDTH = self.W_SCREEN - 2 * self.TECH_LEFT_RIGHT_SPACE
		TECH_PANEL_HEIGHT = self.H_SCREEN - 2 * self.TECH_TOP_BOTTOM_SPACE

		self.tradePanel = self.getNextWidgetName()
		screen.addPanel( self.tradePanel, "", "", True, True
					   , TECH_PANEL_X, TECH_PANEL_Y, TECH_PANEL_WIDTH, TECH_PANEL_HEIGHT
					   , PanelStyles.PANEL_STYLE_MAIN )

		self.techIconGrid.createGrid()

		self.techIconGrid.clearData()
		tradeData = TradeData()
		tradeData.ItemType = TradeableItems.TRADE_TECHNOLOGIES
		currentRow = 0

		for iLoopPlayer in range(gc.getMAX_PLAYERS()):
			currentPlayer = gc.getPlayer(iLoopPlayer)
			iLoopTeam = currentPlayer.getTeam()
			currentTeam = gc.getTeam(iLoopTeam)

			if ( currentPlayer.isAlive() and not currentPlayer.isBarbarian() and not currentPlayer.isMinorCiv() 
										 and gc.getTeam(currentPlayer.getTeam()).isHasMet(activePlayer.getTeam()) 
										 and iLoopPlayer != self.iActiveLeader ):
				message = ""
				if ( not gc.getTeam(activePlayer.getTeam()).isTechTrading() and not gc.getTeam(currentPlayer.getTeam()).isTechTrading() ):
					message = localText.getText("TXT_KEY_FOREIGN_ADVISOR_NO_TECH_TRADING", ())

				self.techIconGrid.appendRow(currentPlayer.getName(), message)
				self.techIconGrid.addIcon( currentRow, iTechColLeader, gc.getLeaderHeadInfo(currentPlayer.getLeaderType()).getButton()
										 , 64, WidgetTypes.WIDGET_LEADERHEAD, iLoopPlayer, self.iActiveLeader )

# BUG - AI status - end
				zsStatus = ""
				if not DiplomacyUtil.isWillingToTalk(currentPlayer, activePlayer):
					zsStatus += u"!"

				if (currentTeam.isAtWar(iActiveTeam)):
					zsStatus += self.WAR_ICON
				elif (currentTeam.isForcePeace(iActiveTeam)):
					zsStatus += self.PEACE_ICON

				self.techIconGrid.setText(currentRow, iTechColStatus, zsStatus)
# BUG - AI status - end

				if (gc.getTeam(activePlayer.getTeam()).isGoldTrading() or gc.getTeam(currentPlayer.getTeam()).isGoldTrading()):
					sAmount = str(gc.getPlayer(iLoopPlayer).AI_maxGoldTrade(self.iActiveLeader))
					self.techIconGrid.setText(currentRow, iTechColGold, sAmount)

				if (gc.getTeam(activePlayer.getTeam()).isTechTrading() or gc.getTeam(currentPlayer.getTeam()).isTechTrading() ):

					for iLoopTech in range(gc.getNumTechInfos()):
					
						tradeData.iData = iLoopTech
						if (activePlayer.canTradeItem(iLoopPlayer, tradeData, False) and activePlayer.getTradeDenial(iLoopPlayer, tradeData) == DenialTypes.NO_DENIAL): # wants
							self.techIconGrid.addIcon( currentRow, iTechColWants, gc.getTechInfo(iLoopTech).getButton()
																				 , 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
						elif (gc.getTeam(activePlayer.getTeam()).isHasTech(iLoopTech) and currentPlayer.canResearch(iLoopTech, False)):
							self.techIconGrid.addIcon( currentRow, iTechColCantYou, gc.getTechInfo(iLoopTech).getButton()
																					 , 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
						elif currentPlayer.canResearch(iLoopTech, False):
							self.techIconGrid.addIcon( currentRow, iTechColResearch, gc.getTechInfo(iLoopTech).getButton()
																			, 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
						
						if (currentPlayer.canTradeItem(self.iActiveLeader, tradeData, False)):
							if (currentPlayer.getTradeDenial(self.iActiveLeader, tradeData) == DenialTypes.NO_DENIAL): # will trade
								self.techIconGrid.addIcon( currentRow, iTechColWill, gc.getTechInfo(iLoopTech).getButton()
																					 , 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )
							else: # won't trade
								self.techIconGrid.addIcon( currentRow, iTechColWont, gc.getTechInfo(iLoopTech).getButton()
																					 , 64, *BugDll.widget("WIDGET_PEDIA_JUMP_TO_TECH_TRADE", iLoopTech, iLoopPlayer, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech, -1) )
						elif (gc.getTeam(currentPlayer.getTeam()).isHasTech(iLoopTech) and activePlayer.canResearch(iLoopTech, False)):
							self.techIconGrid.addIcon( currentRow, iTechColCantThem, gc.getTechInfo(iLoopTech).getButton()
																					 , 64, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iLoopTech )

				currentRow += 1
		self.techIconGrid.refresh()



	def initTechTable(self):
		screen = self.getScreen()
		
		gridX = self.MIN_LEFT_RIGHT_SPACE + 10
		gridY = self.MIN_TOP_BOTTOM_SPACE + 10
		gridWidth = self.W_SCREEN - self.MIN_LEFT_RIGHT_SPACE * 2 - 20
		gridHeight = self.H_SCREEN - self.MIN_TOP_BOTTOM_SPACE * 2 - 20
		
		columns = ( IconGrid_BUG.GRID_ICON_COLUMN,
					IconGrid_BUG.GRID_TEXT_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_TEXT_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN,
					IconGrid_BUG.GRID_MULTI_LIST_COLUMN)
		self.techIconGridName = self.getNextWidgetName()
		self.techIconGrid = IconGrid_BUG.IconGrid_BUG( self.techIconGridName, screen, gridX, gridY, gridWidth, gridHeight
											 , columns, self.TECH_USE_SMALL_ICONS, self.SHOW_LEADER_NAMES, self.SHOW_ROW_BORDERS )

		self.techIconGrid.setGroupBorder(self.GROUP_BORDER)
		self.techIconGrid.setGroupLabelOffset(self.GROUP_LABEL_OFFSET)
		self.techIconGrid.setMinColumnSpace(self.MIN_COLUMN_SPACE)
		self.techIconGrid.setMinRowSpace(self.MIN_ROW_SPACE)

#		self.techIconGrid.setHeader( iTechColLeader, localText.getText("TXT_KEY_FOREIGN_ADVISOR_LEADER", ()) )
#		self.techIconGrid.setHeader( iTechColStatus, "" )
		self.techIconGrid.setTextColWidth( iTechColStatus, self.TECH_STATUS_COL_WIDTH )
		self.techIconGrid.setHeader( iTechColWants, localText.getText("TXT_KEY_FOREIGN_ADVISOR_WANTS", ()) )
		self.techIconGrid.setHeader( iTechColCantYou, localText.getText("TXT_KEY_FOREIGN_ADVISOR_CANT_TRADE", ()) )
		self.techIconGrid.setHeader( iTechColResearch, localText.getText("TXT_KEY_FOREIGN_ADVISOR_CAN_RESEARCH", ()) )
		self.techIconGrid.setHeader( iTechColGold, (u"%c" % gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar()) )
		self.techIconGrid.setTextColWidth( iTechColGold, self.TECH_GOLD_COL_WIDTH )
		self.techIconGrid.setHeader( iTechColWill, localText.getText("TXT_KEY_FOREIGN_ADVISOR_FOR_TRADE_2", ()) )
		self.techIconGrid.setHeader( iTechColWont, localText.getText("TXT_KEY_FOREIGN_ADVISOR_NOT_FOR_TRADE_2", ()) )
		self.techIconGrid.setHeader( iTechColCantThem, localText.getText("TXT_KEY_FOREIGN_ADVISOR_CANT_TRADE", ()) )
		
		gridWidth = self.techIconGrid.getPrefferedWidth()
		gridHeight = self.techIconGrid.getPrefferedHeight()
		self.TECH_LEFT_RIGHT_SPACE = (self.W_SCREEN - gridWidth - 20) / 2
		self.TECH_TOP_BOTTOM_SPACE = (self.H_SCREEN - gridHeight - 20) / 2
		gridX = self.TECH_LEFT_RIGHT_SPACE + 10
		gridY = self.TECH_TOP_BOTTOM_SPACE + 10
		
		self.techIconGrid.setPosition(gridX, gridY)
		self.techIconGrid.setSize(gridWidth, gridHeight)
		
##########################################
### END CHANGES ENHANCED INTERFACE MOD ###
##########################################
					
	# Handles the input for this screen...
	def handleInput (self, inputClass):

## Platy Foreign Start ##
		if inputClass.getData1() > 1800 and  inputClass.getData1() < 1810:
			self.handlePlatyToggleRelationshipsCB(inputClass.getData1())
			return
## Platy Foreign End ##
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
			if (inputClass.getButtonType() == WidgetTypes.WIDGET_LEADERHEAD or BugDll.isWidgetVersion(2, inputClass.getButtonType(), "WIDGET_LEADERHEAD_RELATIONS")):
				if (inputClass.getFlags() & MouseFlags.MOUSE_LBUTTONUP):
					self.iSelectedLeader = inputClass.getData1()
					self.drawContents(False)
					return 1
				elif (inputClass.getFlags() & MouseFlags.MOUSE_RBUTTONUP):
					if inputClass.getData1() != self.iActiveLeader:
						self.getScreen().hideScreen()
						return 1
			elif (inputClass.getFunctionName() == self.GLANCE_BUTTON):
				self.handlePlusMinusToggle()
				return 1
############################################
### BEGIN CHANGES ENHANCED INTERFACE MOD ###
############################################
			elif (inputClass.getButtonType() == WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS):
#				ExoticForPrint ("FOOOOOO!!!!")
				pass
##########################################
### END CHANGES ENHANCED INTERFACE MOD ###
##########################################
		
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED):
			if (inputClass.getFunctionName() + str(inputClass.getID()) == self.getWidgetName(self.DEBUG_DROPDOWN_ID)):
				print 'debug dropdown event'
				szName = self.getWidgetName(self.DEBUG_DROPDOWN_ID)
				iIndex = self.getScreen().getSelectedPullDownID(szName)
				self.iActiveLeader = self.getScreen().getPullDownData(szName, iIndex)
				self.drawContents(False)
## Surplus Type Start ##
			if (inputClass.getFunctionName() == "PlatySurplus"):
				self.handlePlatySurplus(inputClass.getData())
## Surplus Type End ##
		elif (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CHARACTER):
			if (inputClass.getData() == int(InputTypes.KB_LSHIFT) or inputClass.getData() == int(InputTypes.KB_RSHIFT)):
				self.iShiftKeyDown = inputClass.getID()
				return 1
		
		if (self.iScreen == self.SCREEN_DICT["BONUS"]):
			return self.resIconGrid.handleInput(inputClass)
		elif (self.iScreen == self.SCREEN_DICT["TECH"]):
			return self.techIconGrid.handleInput(inputClass)

		return 0



## Surplus Type ##
	def handlePlatySurplus ( self, argsList ) :
		self.iSurplus = int(argsList) - 1
		self.drawContents(True)
		return 1
## Platy Foreign Start ##

	def handlePlatyToggleRelationshipsCB ( self, iData1):
		if iData1 == 1801:
			self.bContactLine = not self.bContactLine
		elif iData1 == 1802:
			self.bWarLine = not self.bWarLine
		elif iData1 == 1803:
			self.bDefensiveLine = not self.bDefensiveLine
		elif iData1 == 1804:
			self.bOpenBorderLine = not self.bOpenBorderLine
		elif iData1 == 1805:
			self.bTeamLine = not self.bTeamLine
		elif iData1 == 1806:
			self.bVassalLine = not self.bVassalLine
		elif iData1 == 1807:
			self.bHideVassal = not self.bHideVassal
		elif iData1 == 1808:
			self.bHideTeam = not self.bHideTeam
		self.drawContents(True)
		return 1
## Platy Foreign End ##

	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount * 4 + self.iScreen)
		self.nWidgetCount += 1
		return szName
											
	def getNextLineName(self):
		szName = self.LINE_ID + str(self.nLineCount * 4 + self.iScreen)
		self.nLineCount += 1
		return szName
											
	def getWidgetName(self, szBaseName):
		szName = szBaseName + str(self.iScreen)
		return szName
		
	def clearAllLines(self):
		screen = self.getScreen()
		nLines = self.nLineCount
		self.nLineCount = 0
		for i in range(nLines):
			screen.removeLineGFC(self.BACKGROUND_ID, self.getNextLineName())
		self.nLineCount = 0	
		
	def deleteAllWidgets(self):
		screen = self.getScreen()
		i = self.nWidgetCount - 1
		while (i >= 0):
			self.nWidgetCount = i
			screen.deleteWidget(self.getNextWidgetName())
			i -= 1

		self.nWidgetCount = 0
		self.clearAllLines()

	def killScreen(self):
		if (self.iScreen >= 0):
			screen = self.getScreen()
			screen.hideScreen()
			self.iScreen = -1
		return

	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME + str(self.iScreen), CvScreenEnums.FOREIGN_ADVISOR)

	def update(self, fDelta):
		if (CyInterface().isDirty(InterfaceDirtyBits.Foreign_Screen_DIRTY_BIT) == True):
			CyInterface().setDirty(InterfaceDirtyBits.Foreign_Screen_DIRTY_BIT, False)
			self.drawContents(False)
		return
	def drawLinks (self):
		screen = self.getScreen()
		xLink = self.DX_LINK / 2;
		for i in range (len (self.ORDER_LIST)):
			szTextId = self.getNextWidgetName()
			szScreen = self.ORDER_LIST[i]
			if (self.iScreen != self.SCREEN_DICT[szScreen]):
				screen.setText (szTextId, "", u"<font=4>" + localText.getText (self.TXT_KEY_DICT[szScreen], ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, xLink, self.Y_LINK, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_FOREIGN_ADVISOR, self.SCREEN_DICT[szScreen], -1)
			else:
				screen.setText (szTextId, "", u"<font=4>" + localText.getColorText (self.TXT_KEY_DICT[szScreen], (), gc.getInfoTypeForString ("COLOR_YELLOW")).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, xLink, self.Y_LINK, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_FOREIGN_ADVISOR, -1, -1)
			xLink += self.DX_LINK

	def handlePlatyHideLeadersCB ( self, argsList ) :
		CvForeignAdvisor.CvForeignAdvisor.deleteAllWidgets(self)
		screen = self.getScreen()
		screen.setLabel(self.getNextWidgetName(), "", self.SCREEN_TITLE, CvUtil.FONT_CENTER_JUSTIFY, self.W_SCREEN / 2, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		self.drawLinks()
		CvForeignAdvisor.CvForeignAdvisor.drawLegend(self, False)
		CvForeignAdvisor.CvForeignAdvisor.drawLeaders(self)
		CvForeignAdvisor.CvForeignAdvisor.drawLines(self)
		return 1
## Platy Foreign End ##

def smallText (text):
	return u"<font=2>%s</font>" % text

def smallSymbol (symbol):
	return smallText(FontUtil.getChar(symbol))
	
