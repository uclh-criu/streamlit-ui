import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"

interface State {
  isFocused: boolean
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class ConceptView extends StreamlitComponentBase<State> {
  public state = { isFocused: false }

  private renderValue(value: any): ReactNode {
    if (typeof value === "object" && value !== null) {
      return this.renderObject(value)
    }
    return <span>{String(value)}</span>
  }

  private renderObject(obj: any): ReactNode {
    return (
      <div style={{ marginLeft: "10px" }}>
        {Object.entries(obj).map(([key, value]) => (
          <div key={key}>
            <strong>{key}:</strong> {this.renderValue(value)}
          </div>
        ))}
      </div>
    )
  }
  public render = (): ReactNode => {
    // Arguments that are passed to the plugin in Python are accessible
    const object = this.props.args["object"]
    const { theme } = this.props
    const style: React.CSSProperties = {}

    Streamlit.setComponentValue(false)

    // Maintain compatibility with older versions of Streamlit that don't send
    // a theme object.
    if (theme) {
      // Use the theme object to style our button border. Alternatively, the
      // theme style is defined in CSS vars.
      const borderStyling = `1px solid ${
        this.state.isFocused ? theme.primaryColor : "gray"
      }`
      style.border = borderStyling
      style.outline = borderStyling
    }
    return (
      <div
        style={{
          backgroundColor: "white",
          padding: "10px",
          borderRadius: "2px",
          border: "solid 1px gray",
          marginBottom: "10px",
          filter: "drop-shadow(2px 2px lightgray)",
          fontFamily: "ui-monospace",
        }}
      >
        {this.renderValue(object)}
      </div>
    )
  }

  // /** Focus handler for our "Click Me!" button. */
  // private _onFocus = (): void => {
  //   this.setState({ isFocused: true })
  // }

  // /** Blur handler for our "Click Me!" button. */
  // private _onBlur = (): void => {
  //   this.setState({ isFocused: false })
  // }
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(ConceptView)
