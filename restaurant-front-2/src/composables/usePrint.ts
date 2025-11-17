import { ref } from 'vue'

export interface PrintOptions {
  title?: string
  onBeforePrint?: () => void
  onAfterPrint?: () => void
}

export function usePrint() {
  const isPrinting = ref(false)

  /**
   * Print the contents of a specific element
   * @param elementId The ID of the element to print
   * @param options Print options
   */
  function printElement(elementId: string, options: PrintOptions = {}) {
    const element = document.getElementById(elementId)
    if (!element) {
      console.error(`Element with ID "${elementId}" not found`)
      return
    }

    isPrinting.value = true

    if (options.onBeforePrint) {
      options.onBeforePrint()
    }

    // Clone the element to avoid modifying the original
    const printContent = element.cloneNode(true) as HTMLElement

    // Create a temporary iframe for printing
    const iframe = document.createElement('iframe')
    iframe.style.position = 'absolute'
    iframe.style.width = '0'
    iframe.style.height = '0'
    iframe.style.border = 'none'
    document.body.appendChild(iframe)

    const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document
    if (!iframeDoc) {
      console.error('Failed to access iframe document')
      document.body.removeChild(iframe)
      isPrinting.value = false
      return
    }

    // Write the content to the iframe
    iframeDoc.open()
    iframeDoc.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${options.title || 'Imprimir'}</title>
          <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }

            body {
              font-family: 'Courier New', monospace;
              font-size: 12px;
              line-height: 1.4;
              color: #000;
              padding: 12px;
            }

            @page {
              margin: 0;
              size: 80mm auto;
            }

            @media print {
              body {
                margin: 0;
                padding: 12px;
              }
            }

            .print-header {
              text-align: center;
              border-bottom: 2px dashed #000;
              padding-bottom: 8px;
              margin-bottom: 12px;
            }

            .print-header h1 {
              font-size: 18px;
              font-weight: bold;
              margin-bottom: 4px;
            }

            .print-header p {
              font-size: 11px;
              margin: 2px 0;
            }

            .print-section {
              margin-bottom: 12px;
              padding-bottom: 8px;
              border-bottom: 1px dashed #000;
            }

            .print-section:last-child {
              border-bottom: 2px dashed #000;
            }

            .print-row {
              display: flex;
              justify-content: space-between;
              margin: 4px 0;
            }

            .print-label {
              font-weight: bold;
            }

            .print-items {
              margin: 8px 0;
            }

            .print-item {
              margin: 6px 0;
              padding: 4px 0;
            }

            .print-item-name {
              font-weight: bold;
              font-size: 13px;
            }

            .print-item-details {
              display: flex;
              justify-content: space-between;
              font-size: 11px;
              margin-top: 2px;
            }

            .print-total {
              font-size: 14px;
              font-weight: bold;
              margin-top: 8px;
              padding-top: 8px;
              border-top: 2px solid #000;
            }

            .print-footer {
              text-align: center;
              margin-top: 16px;
              padding-top: 8px;
              border-top: 2px dashed #000;
              font-size: 11px;
            }

            .station-badge {
              display: inline-block;
              padding: 2px 6px;
              border: 1px solid #000;
              font-size: 10px;
              border-radius: 3px;
              margin-left: 4px;
              font-weight: bold;
            }

            .status-badge {
              display: inline-block;
              padding: 2px 6px;
              border: 1px solid #000;
              font-size: 10px;
              border-radius: 3px;
            }
          </style>
        </head>
        <body>
          ${printContent.innerHTML}
        </body>
      </html>
    `)
    iframeDoc.close()

    // Wait for content to load, then print
    iframe.onload = () => {
      setTimeout(() => {
        try {
          iframe.contentWindow?.focus()
          iframe.contentWindow?.print()
        } catch (error) {
          console.error('Print error:', error)
        } finally {
          // Clean up after printing
          setTimeout(() => {
            document.body.removeChild(iframe)
            isPrinting.value = false
            if (options.onAfterPrint) {
              options.onAfterPrint()
            }
          }, 100)
        }
      }, 250)
    }
  }

  /**
   * Direct browser print (fallback)
   */
  function printWindow() {
    window.print()
  }

  return {
    isPrinting,
    printElement,
    printWindow,
  }
}
